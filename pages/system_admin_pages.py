from flask import Blueprint, flash, redirect, render_template, request, session

from db.study_models import Study, Studies, InvalidEncryptionKeyError,\
    StudyAlreadyExistsError
from db.user_models import Admin, Admins
from libs.admin_authentication import authenticate_system_admin,\
    get_admins_allowed_studies, admin_is_system_admin,\
    authenticate_admin_study_access
from libs.http_utils import checkbox_to_boolean, combined_multi_dict_to_dict,\
    string_to_int
from config.constants import CHECKBOX_TOGGLES, TIMER_VALUES

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

@system_admin_pages.route('/manage_studies', methods=['GET'])
@authenticate_system_admin
def manage_studies():
    return render_template('manage_studies.html', studies=Studies(),
                           allowed_studies=get_admins_allowed_studies(),
                           system_admin=admin_is_system_admin())


@system_admin_pages.route('/edit_study/<string:study_id>', methods=['GET'])
@authenticate_system_admin
def edit_study(study_id=None):
    return render_template('edit_study.html', study=Study(study_id),
                           all_admins=Admins(),
                           allowed_studies=get_admins_allowed_studies(),
                           system_admin=admin_is_system_admin())


@system_admin_pages.route('/create_study', methods=['GET', 'POST'])
@authenticate_system_admin
def create_study():
    if request.method == 'GET':
        return render_template('create_study.html')
    name = request.form.get('name')
    encryption_key = request.form.get('encryption_key')
    try:
        study = Study.create_default_study(name, encryption_key)
        flash("Successfully created a new study.", 'success')
        return redirect('/device_settings/' + str(study._id))
    except (InvalidEncryptionKeyError, StudyAlreadyExistsError) as e:
        flash(e.message, 'danger')
        return redirect('/create_study')


@system_admin_pages.route('/device_settings/<string:study_id>', methods=['GET', 'POST'])
@authenticate_admin_study_access
@authenticate_system_admin
def device_settings(study_id=None):
    study = Study(study_id)
    if request.method == 'GET':
        settings = study.get_study_device_settings()
        return render_template("device_settings.html", settings=settings,
                               study_id=str(study_id) )
    settings = study.get_study_device_settings()
    params = combined_multi_dict_to_dict( request.values )
    params = checkbox_to_boolean(CHECKBOX_TOGGLES, params)
    params = string_to_int(TIMER_VALUES, params)
    settings.update(**params)
    return redirect('/edit_study/' + str(study._id))
