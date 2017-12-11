import os
import jinja2
from flask import Flask, render_template, redirect
from werkzeug.contrib.fixers import ProxyFix
from pages import admin_pages, mobile_pages, survey_designer, system_admin_pages,\
    data_access_web_form
from api import admin_api, copy_study_api, data_access_api, data_pipeline_api, mobile_api, survey_api
from libs.admin_authentication import is_logged_in
from libs.security import set_secret_key
from config.secure_settings import SENTRY_DSN, SENTRY_JAVASCRIPT_DSN


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
app.register_blueprint(survey_api.survey_api)
app.register_blueprint(data_access_api.data_access_api)
app.register_blueprint(data_access_web_form.data_access_web_form)
app.register_blueprint(copy_study_api.copy_study_api)
app.register_blueprint(data_pipeline_api.data_pipeline_api)


if SENTRY_DSN != "USE_EMAIL_FALLBACK":
    from raven.contrib.flask import Sentry
    sentry = Sentry(app, dsn=SENTRY_DSN)


@app.route("/<page>.html")
def strip_dot_html(page):
    #strips away the dot html from pages
    return redirect("/%s" % page)


@app.context_processor
def inject_dict_for_all_templates():
    return {"SENTRY_JAVASCRIPT_DSN":SENTRY_JAVASCRIPT_DSN}


#Extra Production settings
if not __name__ == '__main__':
    # Points our custom 404 page (in /frontend/templates) to display on a 404 error
    @app.errorhandler(404)
    def e404(e):
        return render_template("404.html",is_logged_in=is_logged_in()), 404

#Extra Debugging settings
if __name__ == '__main__':
    # might be necessary if running on windows/linux subsystem on windows.
    # from gevent.wsgi import WSGIServer
    # http_server = WSGIServer(('', 8080), app)
    # http_server.serve_forever()
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", "8080")), debug=True)

