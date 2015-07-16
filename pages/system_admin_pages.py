from bson import ObjectId
from flask import Blueprint, flash, redirect, render_template, request, session

from db.study_models import Study, Studies
from db.user_models import Admin, Admins
from libs.admin_authentication import authenticate_system_admin,\
    get_admins_allowed_studies, admin_is_system_admin

system_admin_pages = Blueprint('system_admin_pages', __name__)


@system_admin_pages.route('/manage_admins', methods=['GET'])
@authenticate_system_admin
def manage_admins():
    admins = []
    for admin in Admins():
        admin_name = admin._id
        allowed_studies = Studies(admins=admin._id, field='name')
        admins.append((admin_name, allowed_studies))
    return render_template('manage_admins.html', admins=admins,
                           allowed_studies=get_admins_allowed_studies(),
                           system_admin=admin_is_system_admin())


@system_admin_pages.route('/edit_admin/<string:admin_id>', methods=['GET','POST'])
@authenticate_system_admin
def edit_admin(admin_id):
    admin = Admin(admin_id)
    admin_is_current_user = (admin._id == session['admin_username'])
    return render_template('edit_admin.html', admin=admin,
                           current_studies=Studies(admins=admin._id),
                           all_studies=Studies(),
                           allowed_studies=get_admins_allowed_studies(),
                           admin_is_current_user=admin_is_current_user,
                           system_admin=admin_is_system_admin())


@system_admin_pages.route('/create_new_researcher', methods=['GET', 'POST'])
@authenticate_system_admin
def create_new_researcher():
    if request.method == 'GET':
        return render_template('create_new_researcher.html',
                               allowed_studies=get_admins_allowed_studies(),
                               system_admin=admin_is_system_admin())
    admin_id = request.form.get('admin_id')
    password = request.form.get('password')
    if Admins(_id=admin_id):
        flash("There is already a researcher with username " + admin_id, 'danger')
        return redirect('/create_new_researcher')
    else:
        admin = Admin.create(admin_id, password)
        return redirect('/edit_admin/' + admin._id)


"""########################### Study Pages ##################################"""
""""TODO: Alvin/Josh. implement this page, point the post function at /create_new_study,
see the create_new_study function in admin_api for details.
Page should include a paraphrase of "enter encryption key here for the study, all
user data stored by server will require this password, strongly recommend you use a
true random source, for instance random.org"""
@system_admin_pages.route('/new_study', methods=["GET"])
@authenticate_system_admin
def render_make_new_study():
    return render_template("fill_me_in_:D")


@system_admin_pages.route('/edit_study_device_settings/<string:study_id>', methods=["GET"])
@authenticate_system_admin
def render_edit_study_device_settings(study_id=None):
    study = Study(ObjectId(study_id))
    settings = study.get_study_device_settings()
    return render_template("edit_device_settings.html",
                           settings=settings,
                           study_id=study_id)