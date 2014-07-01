from flask import Flask, render_template, ., redirect, request
import sys, jinja2, traceback
from utils.logging import log_error
from utils.security import set_secret_key
from frontend import templating, auth
from pages import mobile_api, admin

def subdomain(directory):
    app = Flask(__name__, static_folder=directory + "/static")
    set_secret_key(app)
    loader = [app.jinja_loader, jinja2.FileSystemLoader(directory + "/templates")]
    app.jinja_loader = jinja2.ChoiceLoader(loader)
    return app

#Register pages here
app = subdomain("frontend")
app.register_blueprint(mobile_api.mobile_api)
app.register_blueprint(admin.admin)
app.register_blueprint(survey_builder.survey_builder)

@app.route("/<page>.html")
def strip_dot_html(page):
    #strips away the dot html from pages
    return redirect("/%s" % page)

@app.errorhandler(404)
def e404(e):
    return render_template("404.html")

@app.errorhandler(500)
def e500_text(e):
    try:
        stacktrace = traceback.format_exc()
        print(stacktrace)
    except Exception as e:
        log_error(e)
    return render_template("500.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)