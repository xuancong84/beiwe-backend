from flask import Flask, render_template, url_for, redirect, request
import sys, jinja2, traceback
from utils.logging import log_error

app = Flask(__name__)

@app.route('/')
@app.route("/index/")
def hello_world():
    return 'Hello World!'

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


if __name__ == '__main__':
    app.run()