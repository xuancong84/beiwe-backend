from csv import writer
from re import sub

from flask import *

from libs.admin_authentication import *
from libs.s3 import s3_upload, create_client_key_pair
from libs.streaming_bytes_io import StreamingBytesIO
from database.models import Participant, Study
from config.settings import DOMAIN_NAME
import base64, qrcode
from io import BytesIO

participant_administration = Blueprint('participant_administration', __name__)


@participant_administration.route('/reset_participant_password', methods=["POST"])
@authenticate_admin_study_access
def reset_participant_password():
    """ Takes a patient ID and resets its password. Returns the new random password."""
    patient_id = request.values['patient_id']
    study_id = request.values['study_id']
    participant_set = Participant.objects.filter(patient_id=patient_id)
    if participant_set.exists() and str(participant_set.values_list('study', flat=True).get()) == study_id:
        participant = participant_set.get()
        new_password = participant.reset_password()
        flash('Patient {:s}\'s password has been reset to {:s}.'.format(patient_id, new_password), 'success')
    else:
        flash('Sorry, something went wrong when trying to reset the patient\'s password.', 'danger')

    if not isPatientRegistered(study_id, patient_id):
        return make_QR(study_id, patient_id, new_password, session["timezone"])

    return redirect('/view_study/{:s}'.format(study_id))


@participant_administration.route('/reset_device', methods=["POST"])
@authenticate_admin_study_access
def reset_device():
    """
    Resets a participant's device. The participant will not be able to connect until they register a new device.
    """

    patient_id = request.values['patient_id']
    study_id = request.values['study_id']
    participant_set = Participant.objects.filter(patient_id=patient_id)
    if participant_set.exists() and str(participant_set.values_list('study', flat=True).get()) == study_id:
        participant = participant_set.get()
        participant.clear_device()
        flash('For patient {:s}, device was reset; password is untouched.'.format(patient_id), 'success')
    else:
        flash('Sorry, something went wrong when trying to reset the patient\'s device.', 'danger')

    return redirect('/view_study/{:s}'.format(study_id))


@participant_administration.route('/create_new_patient', methods=["POST"])
@authenticate_admin_study_access
def create_new_patient():
    """
    Creates a new user, generates a password and keys, pushes data to s3 and user database, adds user to
    the study they are supposed to be attached to and returns a string containing password and patient id.
    """

    study_id = request.values['study_id']
    patient_id, password = Participant.create_with_password(study_id=study_id)

    # Create an empty file on S3 indicating that this user exists
    study_object_id = Study.objects.filter(pk=study_id).values_list('object_id', flat=True).get()
    s3_upload(patient_id, "", study_object_id)
    create_client_key_pair(patient_id, study_object_id)

    flash('Created a new participant with patient_id: %s , password: %s'%(patient_id, password), 'success')
    return make_QR(study_id, patient_id, password, timezone=session["timezone"])


@participant_administration.route('/check_new_patient/<string:study_id>/<string:patient_id>', methods=["GET"])
@authenticate_admin_study_access
def check_new_patient(study_id=None, patient_id=None):
    return Response('yes' if isPatientRegistered(study_id, patient_id) else 'no', mimetype='text/plain')


@participant_administration.route('/create_many_patients/<string:study_id>', methods=["POST"])
@authenticate_admin_study_access
def create_many_patients(study_id=None):
    """ Creates a number of new users at once for a study.  Generates a password and keys for
    each one, pushes data to S3 and the user database, adds users to the study they're supposed
    to be attached to, and returns a CSV file for download with a mapping of Patient IDs and passwords. """

    number_of_new_patients = int(request.form.get('number_of_new_patients', 0))
    desired_filename = request.form.get('desired_filename', '')
    filename_spaces_to_underscores = sub(r'[\ =]', '_', desired_filename)
    filename = sub(r'[^a-zA-Z0-9_\.=]', '', filename_spaces_to_underscores)
    if not filename.endswith('.csv'):
        filename += ".csv"
    return Response(csv_generator(study_id, number_of_new_patients),
                    mimetype="csv",
                    headers={'Content-Disposition': 'attachment; filename="%s"' % filename})


def csv_generator(study_id, number_of_new_patients):
    si = StreamingBytesIO()
    filewriter = writer(si)
    filewriter.writerow(['Patient ID', "Registration password"])
    study_object_id = Study.objects.filter(pk=study_id).values_list('object_id', flat=True).get()
    for _ in xrange(number_of_new_patients):
        patient_id, password = Participant.create_with_password(study_id=study_id)
        # Creates an empty file on s3 indicating that this user exists
        s3_upload(patient_id, "", study_object_id)
        create_client_key_pair(patient_id, study_object_id)
        filewriter.writerow([patient_id, password])
        yield si.getvalue()
        si.empty()


def make_QR(study_id, patient_id, password, timezone=0):
    image = qrcode.make('{"url":"%s", "uid":"%s", "utp":"%s"}'%(DOMAIN_NAME, patient_id, password))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    img_base64 = "data:image/jpeg;base64," + img_str

    study = Study.objects.get(pk=study_id)
    tracking_survey_ids = study.get_survey_ids_and_object_ids_for_study('tracking_survey')
    audio_survey_ids = study.get_survey_ids_and_object_ids_for_study('audio_survey')
    participants = study.participants.all()

    return render_template(
        'view_study.html',
        study=study,
        TZ=timezone,
        qr_image=img_base64,
        check_id=patient_id,
        patients=participants,
        audio_survey_ids=audio_survey_ids,
        tracking_survey_ids=tracking_survey_ids,
        allowed_studies=get_admins_allowed_studies(),
        system_admin=admin_is_system_admin()
    )


def isPatientRegistered(study_id, patient_id):
    """
    Check whether a user with patient_id in study_id has registered, returns yes or no.
    """
    try:
        participant = Participant.objects.get(patient_id=patient_id)
        isReg = (participant.device_id != '' and str(participant.study_id) == study_id)
    except:
        isReg = False
    return isReg

