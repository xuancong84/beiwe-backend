import json

from flask import abort, Blueprint, flash, redirect, render_template, request,\
    session

from config.constants import CHECKBOX_TOGGLES, TIMER_VALUES
from libs.admin_authentication import authenticate_system_admin,\
    get_admins_allowed_studies, admin_is_system_admin,\
    authenticate_admin_study_access
from libs.copy_study import copy_existing_study_if_asked_to
from libs.http_utils import checkbox_to_boolean, combined_multi_dict_to_dict,\
    string_to_int

# Mongolia models
from db.study_models import Study, InvalidEncryptionKeyError,\
    StudyAlreadyExistsError

# Django models
from study.models import Researcher, Study as DStudy

system_admin_pages = Blueprint('system_admin_pages', __name__)

# TODO: Document.


@system_admin_pages.route('/manage_researchers', methods=['GET'])
@authenticate_system_admin
def manage_researchers():
    researcher_list = []
    for researcher in Researcher.get_all_researchers_by_username():
        allowed_studies = DStudy.get_all_studies_by_name().filter(researchers=researcher).values_list('name', flat=True)
        researcher_list.append((researcher.as_native_python(), list(allowed_studies)))

    return render_template(
        'manage_researchers.html',
        admins=json.dumps(researcher_list),
        allowed_studies=get_admins_allowed_studies(),
        system_admin=admin_is_system_admin()
    )


@system_admin_pages.route('/edit_researcher/<string:researcher_pk>', methods=['GET', 'POST'])
@authenticate_system_admin
def edit_researcher(researcher_pk):
    researcher = Researcher.objects.get(pk=researcher_pk)
    admin_is_current_user = (researcher.username == session['admin_username'])
    # AJK TODO maybe make the default ordering the case-insensitive alphabetical one
    current_studies = DStudy.get_all_studies_by_name().filter(researchers=researcher)
    return render_template(
        'edit_researcher.html',
        admin=researcher,
        current_studies=current_studies,
        all_studies=DStudy.get_all_studies_by_name(),
        allowed_studies=get_admins_allowed_studies(),
        admin_is_current_user=admin_is_current_user,
        system_admin=admin_is_system_admin(),
        redirect_url='/edit_researcher/{:s}'.format(researcher_pk),
    )


@system_admin_pages.route('/create_new_researcher', methods=['GET', 'POST'])
@authenticate_system_admin
def create_new_researcher():
    if request.method == 'GET':
        return render_template(
            'create_new_researcher.html',
            allowed_studies=get_admins_allowed_studies(),
            system_admin=admin_is_system_admin()
        )

    # Drop any whitespace or special characters from the username
    username = ''.join(e for e in request.form.get('admin_id') if e.isalnum())
    password = request.form.get('password')

    if Researcher.objects.filter(username=username).exists():
        flash("There is already a researcher with username " + username, 'danger')
        return redirect('/create_new_researcher')
    else:
        researcher = Researcher.create_with_password(username, password)
        return redirect('/edit_researcher/{:d}'.format(researcher.pk))


"""########################### Study Pages ##################################"""


@system_admin_pages.route('/manage_studies', methods=['GET'])
@authenticate_system_admin
def manage_studies():
    studies = [study.as_native_python() for study in DStudy.get_all_studies_by_name()]
    return render_template(
        'manage_studies.html',
        studies=json.dumps(studies),
        allowed_studies=get_admins_allowed_studies(),
        system_admin=admin_is_system_admin()
    )


@system_admin_pages.route('/edit_study/<string:study_id>', methods=['GET'])
@authenticate_system_admin
def edit_study(study_id=None):
    study = DStudy.objects.get(pk=study_id)
    all_researchers = Researcher.get_all_researchers_by_username()
    return render_template(
        'edit_study.html',
        study=study,
        all_researchers=all_researchers,
        allowed_studies=get_admins_allowed_studies(),
        system_admin=admin_is_system_admin(),
        redirect_url='/edit_study/{:s}'.format(study_id),
    )


@system_admin_pages.route('/create_study', methods=['GET', 'POST'])
@authenticate_system_admin
def create_study():
    if request.method == 'GET':
        studies = [study.as_native_python() for study in DStudy.get_all_studies_by_name()]
        return render_template(
            'create_study.html',
            studies=json.dumps(studies),
            allowed_studies=get_admins_allowed_studies(),
            system_admin=admin_is_system_admin()
        )

    name = request.form.get('name')
    encryption_key = request.form.get('encryption_key')
    try:
        study = DStudy.create_with_object_id(name=name, encryption_key=encryption_key)
        copy_existing_study_if_asked_to(study)
        flash('Successfully created study {}.'.format(name), 'success')
        return redirect('/device_settings/{:d}'.format(study.pk))
    # AJK TODO make sure you're catching the right errors
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
    study = DStudy.objects.get(pk=study_id)
    readonly = not admin_is_system_admin()

    if request.method == 'GET':
        settings = study.get_study_device_settings()
        return render_template(
            "device_settings.html",
            study=study.as_native_python(),
            settings=settings.as_native_python(),
            readonly=not admin_is_system_admin(),
            system_admin=admin_is_system_admin()
        )
    
    if readonly:
        abort(403)
        
    settings = study.get_study_device_settings()
    params = combined_multi_dict_to_dict( request.values )
    params = checkbox_to_boolean(CHECKBOX_TOGGLES, params)
    params = string_to_int(TIMER_VALUES, params)
    settings.update(**params)
    return redirect('/edit_study/{:d}'.format(study.id))
