import os, sys, psycopg2, boto3

from datetime import *
import jinja2, time
from flask import Flask, render_template, redirect
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix

from config import load_django
from config.constants import CHECKABLE_FILES

from api import (participant_administration, admin_api, copy_study_api, data_access_api,
    data_pipeline_api, mobile_api, survey_api)
from config.settings import SENTRY_ELASTIC_BEANSTALK_DSN, SENTRY_JAVASCRIPT_DSN
from libs.admin_authentication import is_logged_in
from libs.security import set_secret_key
from pages import (admin_pages, mobile_pages, survey_designer, system_admin_pages, data_access_web_form)


# # if running locally we want to use a sqlite database
# if __name__ == '__main__':
#     os.environ['DJANGO_DB_ENV'] = "local"
#
# # if running through WSGI we want
# if not __name__ == '__main__':
#     os.environ['DJANGO_DB_ENV'] = "remote"
# Load and set up Django


def subdomain(directory):
    app = Flask(__name__, static_folder=directory + "/static")
    set_secret_key(app)
    loader = [app.jinja_loader, jinja2.FileSystemLoader(directory + "/templates")]
    app.jinja_loader = jinja2.ChoiceLoader(loader)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app


# Register pages here
app = subdomain("frontend")
app.register_blueprint(mobile_api.mobile_api)
app.register_blueprint(admin_pages.admin_pages)
app.register_blueprint(mobile_pages.mobile_pages)
app.register_blueprint(system_admin_pages.system_admin_pages)
app.register_blueprint(survey_designer.survey_designer)
app.register_blueprint(admin_api.admin_api)
app.register_blueprint(participant_administration.participant_administration)
app.register_blueprint(survey_api.survey_api)
app.register_blueprint(data_access_api.data_access_api)
app.register_blueprint(data_access_web_form.data_access_web_form)
app.register_blueprint(copy_study_api.copy_study_api)
app.register_blueprint(data_pipeline_api.data_pipeline_api)

# Don't set up Sentry for local development
if os.environ['DJANGO_DB_ENV'] != 'local':
    sentry = Sentry(app, dsn=SENTRY_ELASTIC_BEANSTALK_DSN)


@app.route("/<page>.html")
def strip_dot_html(page):
    # Strips away the dot html from pages
    return redirect("/%s" % page)


@app.context_processor
def inject_dict_for_all_templates():
    return {"SENTRY_JAVASCRIPT_DSN": SENTRY_JAVASCRIPT_DSN}


@app.template_filter('check_date_elapse')
def check_date_elapse(s_date, date_elapse_color):
    try:
        t1 = time.mktime(s_date.timetuple())
        t2 = time.mktime(datetime.now().timetuple())
        elapse = t2 - t1
        return eval(date_elapse_color, locals())
    except:
        pass
    return 'black'


@app.template_filter('print_date_in_timezone')
def print_date_in_timezone(s_date, TZ):
    try:
        dt = s_date-timedelta(minutes=TZ)
        return '%.19s' % dt
    except:
        try:
            return '%.19s' % s_date
        except:
            pass
    return 'error'


daily_var = {i:0 for i in CHECKABLE_FILES}

@app.template_filter('print_data_completion')
def print_data_completion(patient, study):
    upinfo = patient.get_upload_info()
    cycle_days = study.device_settings.study_cycle_days
    formula = study.device_settings.daily_check_formula
    now_time = datetime.now()
    ret = []
    for dday in range(1, cycle_days+1):
        day_key = '%.10s'%(now_time-timedelta(days=dday))
        try:
            ret += [eval(formula, daily_var, upinfo[day_key])]
        except:
            ret += ['X']
    return ''.join(ret[::-1])


# Extra Debugging settings
if __name__ == '__main__':
    # Test PostgreSQL connection
    try:
        conn = psycopg2.connect(host=os.environ['RDS_HOSTNAME'],
                                database=os.environ['RDS_DB_NAME'],
                                user=os.environ['RDS_USERNAME'],
                                password=os.environ['RDS_PASSWORD'])
        conn.close()
    except:
        print "PostgreSQL server connection failed, continue? (y/n)"
        if raw_input().lower() != 'y':
            sys.exit(1)

    # Test S3 bucket connection
    try:
        conn = boto3.client('s3',
                            endpoint_url=os.environ['S3_ENDPOINT_URL'],
                            aws_access_key_id=os.environ['S3_ACCESS_CREDENTIALS_USER'],
                            aws_secret_access_key=os.environ['S3_ACCESS_CREDENTIALS_KEY'])
        buckets = conn.list_buckets()
        if 'Buckets' not in buckets or \
                os.environ['S3_BUCKET'] not in [d['Name'] for d in buckets['Buckets']]:
            conn.create_bucket(Bucket=os.environ['S3_BUCKET'])
            conn.put_object(Bucket=os.environ['S3_BUCKET'], Key='test-key', Body='test-body')
            obj = conn.get_object(Bucket=os.environ['S3_BUCKET'], Key='test-key')
            assert (obj['Body']._raw_stream.data == 'test-body')
        else:
            obj = conn.get_object(Bucket=os.environ['S3_BUCKET'], Key='test-key')
            assert (obj['Body']._raw_stream.data == 'test-body')
    except:
        print "S3 bucket access failed, continue? (y/n)"
        if raw_input().lower() != 'y':
            sys.exit(1)

    # might be necessary if running on windows/linux subsystem on windows.
    # from gevent.wsgi import WSGIServer
    # http_server = WSGIServer(('', 8080), app)
    # http_server.serve_forever()
    if os.getenv('USE_HTTP') == '1':
        app.run(host='0.0.0.0', port=int(os.getenv("PORT", "80")), debug=False)
    else:
        app.run(host='0.0.0.0', port=int(os.getenv("PORT", "443")), ssl_context=('./ssl/ssl.crt', './ssl/ssl.key'), debug=False)

else:
    # Points our custom 404 page (in /frontend/templates) to display on a 404 error
    @app.errorhandler(404)
    def e404(e):
        return render_template("404.html", is_logged_in=is_logged_in()), 404
