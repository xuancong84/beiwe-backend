from flask import abort, Blueprint, flash, redirect, render_template, request,\
    session
from db.study_models import Study, Studies, InvalidEncryptionKeyError,\
    StudyAlreadyExistsError
from db.user_models import Admin, Admins
from libs.admin_authentication import authenticate_system_admin,\
    get_admins_allowed_studies, admin_is_system_admin,\
    authenticate_admin_study_access
from libs.copy_study import copy_existing_study_if_asked_to
from libs.http_utils import checkbox_to_boolean, combined_multi_dict_to_dict,\
    string_to_int
from config.constants import CHECKBOX_TOGGLES, TIMER_VALUES

system_admin_pages = Blueprint('system_admin_pages', __name__)

# TODO: Document.

@system_admin_pages.route('/manage_admins', methods=['GET'])
@authenticate_system_admin
def manage_admins():
    admins = []
    for admin in Admins():
        admin_name = admin._id
        allowed_studies = ' | '.join(sorted(Studies(admins=admin._id, field='name'),
                                            key=lambda x: x.lower()))
        admins.append((admin_name, allowed_studies))
    admins = sorted(admins, key=lambda s: s[0].lower())
    return render_template('manage_admins.html', admins=admins,
                           allowed_studies=get_admins_allowed_studies(),
                           system_admin=admin_is_system_admin())


@system_admin_pages.route('/edit_admin/<string:admin_id>', methods=['GET','POST'])
@authenticate_system_admin
def edit_admin(admin_id):
    admin = Admin(admin_id)
    admin_is_current_user = (admin._id == session['admin_username'])
    current_studies=sorted(Studies(admins=admin._id), key=lambda x: x.name.lower())
    return render_template('edit_admin.html', admin=admin,
                           current_studies=current_studies,
                           all_studies=Studies.get_all_studies(),
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
    admin_id = ''.join(e for e in request.form.get('admin_id') if e.isalnum())
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
    return render_template('manage_studies.html',
                           studies=Studies.get_all_studies(),
                           allowed_studies=get_admins_allowed_studies(),
                           system_admin=admin_is_system_admin())


@system_admin_pages.route('/edit_study/<string:study_id>', methods=['GET'])
@authenticate_system_admin
def edit_study(study_id=None):
    return render_template('edit_study.html', study=Study(study_id),
                           all_admins=sorted(Admins(), key=lambda x: x._id.lower()),
                           allowed_studies=get_admins_allowed_studies(),
                           system_admin=admin_is_system_admin())


@system_admin_pages.route('/create_study', methods=['GET', 'POST'])
@authenticate_system_admin
def create_study():
    if request.method == 'GET':
        return render_template('create_study.html',
                               studies=Studies.get_all_studies(),
                               allowed_studies=get_admins_allowed_studies(),
                               system_admin=admin_is_system_admin())
    name = request.form.get('name')
    encryption_key = request.form.get('encryption_key')
    is_test = request.form.get('is_test') == 'true'  # 'true' -> True, 'false' -> False
    try:
        study = Study.create_default_study(name, encryption_key, is_test)
        flash("Successfully created a new study.", 'success')
        copy_existing_study_if_asked_to(study)
        return redirect('/device_settings/' + str(study._id))
    except (InvalidEncryptionKeyError, StudyAlreadyExistsError) as e:
        flash(e.message, 'danger')
        return redirect('/create_study')


@system_admin_pages.route('/delete_study/<string:study_id>', methods=['POST'])
@authenticate_system_admin
def delete_study(study_id=None):
    """ This functionality has been disabled pending testing and feature change."""
    if request.form.get('confirmation') == 'true':
        study = Study(study_id)
        study.update({'admins': [],
                      'deleted': True})
    flash ("Deleted study '%s'" % study['name'], 'success')
    return "success"


@system_admin_pages.route('/device_settings/<string:study_id>', methods=['GET', 'POST'])
@authenticate_admin_study_access
def device_settings(study_id=None):
    study = Study(study_id)
    readonly = not admin_is_system_admin()
    if request.method == 'GET':
        settings = study.get_study_device_settings()
        return render_template("device_settings.html",
                               study=study, settings=settings,
                               readonly=not admin_is_system_admin(),
                               system_admin=admin_is_system_admin())
    if readonly: abort(403)
    settings = study.get_study_device_settings()
    params = combined_multi_dict_to_dict( request.values )
    params = checkbox_to_boolean(CHECKBOX_TOGGLES, params)
    params = string_to_int(TIMER_VALUES, params)
    settings.update(**params)
    return redirect('/edit_study/' + str(study._id))
