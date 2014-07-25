'''
Created on Jul 24, 20214

@author: user
'''
from flask import Blueprint, request, abort, send_file
from frontend import templating, auth
from flask import redirect

hello_world = Blueprint('hello_world', __name__)

@hello_world.route('/')
@hello_world.route('/hello_world')
@templating.template('hello_world.html')
def render_main():
    data = {
            #"sms_cohorts": [c for c in Cohorts()],
            #"email_cohorts": [ec for ec in EmailCohorts()]
           }
    return data