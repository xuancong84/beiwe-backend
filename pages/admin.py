from flask import Blueprint, redirect, render_template, request, session
from libs import admin_authentication
from libs.admin_authentication import authenticate_admin_login,\
    authenticate_system_admin, authenticate_admin_study_access
from db.user_models import Users, Admin
from db.study_models import Study, Studies, StudyDeviceSettings,\
    StudyDeviceSettingsCollection
from bson.objectid import ObjectId

admin = Blueprint('admin', __name__)

""" TODO: Eli+Josh.  The following 3 functions have overlapping/duplicated
functionality.  Resolve this. """

#TODO: Josh.  could you please look at this and determine where it should be placed, or even if it is necessary.
"""TODO: josh/alvin: this function provides the admin with users in the studies
they have access to, it is not used anywhere. Maybe this can be on the front 
page for the site, but it's not necessary to use this. """
#@admin.route('/admin_panel') #maybe.
@authenticate_admin_login
def render_surveys():
    """Provides a dict of studies that the current admin has access to by study
    to a flask template."""
    studies = Study.get_studies_for_admin(session['admin_username'])
    users_by_study = {}
    for study in studies:
        users_by_study[study.name] = study.get_participants_in_study()
    return render_template('SOME_PAGE.PROBABLY_HTML', users_by_study=users_by_study)


"""TODO: Josh/Alvin: move this whole function to a render_study() function or
something, and make a new post-login homepage that shows an admin the studies
they have permissions on.  If an admin has permissions on only one page, they
should be automatically redirected to that page upon login."""
@admin.route('/admin_panel', methods=["GET", "POST"])
@authenticate_admin_login
def render_main():
    """ Method responsible rendering admin template"""
    patients = {user['_id']: patient_dict(user) for user in Users()}
    #TODO: Josh, make it use a real study; don't hard-code this.
    main_study = Studies()[0]
    survey_ids = main_study.get_survey_ids_for_study()
    return render_template('admin_panel.html', patients=patients, survey_ids=survey_ids)
 
def patient_dict(patient):
    return {'placeholder_field': 'placeholder field for future data',
            'has_device': patient['device_id'] is not None }


"""########################### Study Pages ##################################"""
""""TODO: Alvin/Josh. implement this page, point the post function at /create_new_study,
see the create_new_study function in admin_api for details.
Page should include a paraphrase of "enter encryption key here for the study, all
user data stored by server will require this password, strongly recommend you use a
true random source, for instance random.org"""
@admin.route('/new_study', methods=["GET"])
@authenticate_system_admin
def render_make_new_study():
    return render_template("fill_me_in_:D")


@admin.route('/edit_study_device_settings/<string:study_id>', methods=["GET"])
#TODO: Eli. confirm that we have both decorators.  do we need a 4th decorator that does exactly this?
#@authenticate_system_admin
@authenticate_admin_study_access
def render_edit_study_device_settings(study_id=None):
    study = Studies(_id=ObjectId(study_id))[0]
    settings = study.get_study_device_settings()
    return render_template("edit_device_settings.html",
                           settings=settings[0],
                           study_id=study_id)


"""########################## Login/Logoff ##################################"""

@admin.route('/')
@admin.route('/admin')
def render_login_page():
    if admin_authentication.is_logged_in():
        return redirect("/admin_panel")
    return render_template('admin_login.html')


@admin.route("/logout")
def logout():
    admin_authentication.logout_loggedin_admin()
    return redirect("/")


@admin.route("/validate_login", methods=["GET", "POST"])
def login():
    """ Authenticates administrator login, redirects to login page
        if authentication fails."""
    if request.method == 'POST':
        username = request.values["username"]
        password = request.values["password"]
        if Admin.check_password(username, password):
            admin_authentication.log_in_admin(username)
            return redirect("/admin_panel")
        return "Username password combination is incorrect. Try again."
    else:
        return redirect("/admin")


@admin.route('/reset_admin_password_form')
@authenticate_admin_login
def render_reset_admin_password_form():
    return render_template('reset_admin_password.html')


@admin.route('/reset_admin_password', methods=['POST'])
@authenticate_admin_login
def reset_admin_password():
    username = session['admin_username']
    current_password = request.values['current_password']
    new_password = request.values['new_password']
    confirm_new_password = request.values['confirm_new_password']
    if not Admin.check_password(username, current_password):
        return 'The "Current Password" you entered is invalid'
    if new_password != confirm_new_password:
        return 'New Password does not match Confirm New Password'
    Admin(username).set_password(new_password)
    return redirect('/')

