from flask import Flask, render_template, url_for, redirect, request
import sys, jinja2, traceback
from utils.logging import log_error
from werkzeug.contrib.fixers import ProxyFix
from frontend import templating, auth

app = Flask(__name__)

@app.route('/')
@app.route("/index/")
def hello_world():
    return 'Hello World!'
#
# @app.route('/', methods=["GET", "POST"])
# @templating.template('admin_login.html')
# def render_login_page():
#     if auth.is_logged_in():
#         return redirect("/main")
#     return {}
#
# @app.route("/validate_login", methods=["POST"])
# def login():
#     username = request.values["username"]
#     password = request.values["password"]
#     if password == "1" and username == "1":
#         auth.login_user()
#         return redirect("/main")
#     return "Username password combination is incorrect. Try again."
#
# @custom.route("/logout")
# def logout():
#     auth.del_loggedin_phonenum()
#     return redirect("/")
#
# @custom.route('/main', methods=["GET", "POST"])
# @auth.authenticated()
# @templating.template('main.html')
# def render_main():
#     data = {
#             #"sms_cohorts": [c for c in Cohorts()],
#             #"email_cohorts": [ec for ec in EmailCohorts()]
#             }
#     return data


@app.route("/<page>.html")
def strip_dot_html(page):
    return redirect("/%s/" % page)

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

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run()