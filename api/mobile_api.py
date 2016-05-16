import calendar, time

from flask import Blueprint, request, abort, render_template, json
from config.constants import ALLOWED_EXTENSIONS
from db.user_models import User
from db.study_models import Study
from libs.encryption import decrypt_device_file, DecryptionKeyError, HandledError
from libs.s3 import s3_upload, get_client_public_key_string, get_client_private_key
from libs.security import PaddingException
from libs.user_authentication import authenticate_user, authenticate_user_registration
from libs.logging import log_error, log_and_email_error, email_system_administrators
from werkzeug.exceptions import BadRequestKeyError
from db.data_access_models import FileToProcess

################################################################################
############################# GLOBALS... #######################################
################################################################################
mobile_api = Blueprint('mobile_api', __name__)

################################################################################
################################ UPLOADS #######################################
################################################################################

@mobile_api.route('/upload', methods=['POST'])
@authenticate_user
def upload():
    """ Entry point to upload GPS, Accelerometer, Audio, PowerState, Calls Log,
        Texts Log, Survey Response, and debugging files to s3.

        Behavior:
        The Beiwe app is supposed to delete the uploaded file if it receives an
        html 200 response.  The API returns a 200 response when the file has A) been
        successfully handled, B) the file it has been sent is empty, C) the file did
        not decrypt properly.  We encountered problems in production with incorrectly
        encrypted files (as well as Android generating "rList" files under unknown
        circumstances) and the app then uploads them.  The source of encryption
        errors is not well understood and could not be tracked down.  In order to
        salvage partial data the server decrypts files to the best of its ability and
        uploads it to S3.  In order to delete these files we still send a 200 response.

        (The above about encryption is awful, in a theoretical version 2.0 the 200
        response would be replaced with a difference response code to allow for
        better debugging and less/fewer ... hax.)

        A 400 error means there is something is wrong with the uploaded file or its
        parameters, administrators will be emailed regarding this upload, the event
        will be logged to the apache log.  The app should not delete the file,
        it should try to upload it again at some point.

        If a 500 error occurs that means there is something wrong server side,
        administrators will be emailed and the event will be logged. The app should
        not delete the file, it should try to upload it again at some point.

        Request format:
        send an http post request to studies.beiwe.org/upload, remember to include
        security parameters (see user_authentication for documentation).
        Provide the contents of the file, encrypted (see encryption specification)
        and properly converted to Base64 encoded text, as a request parameter
        entitled "file".
        Provide the file name in a request parameter entitled "file_name". """
    patient_id = request.values['patient_id']
    user = User(patient_id)
    uploaded_file = request.values['file']
    file_name = request.values['file_name']
#     print "uploaded file name:", file_name, len(uploaded_file)
    if "crashlog" in file_name.lower():
        email_system_administrators(uploaded_file,
                                    "Beiwe Android Crash Log: %s" % user._id,
                                    source_email="android_errors@studies.beiwe.org")
        return render_template('blank.html'), 200

    client_private_key = get_client_private_key(patient_id, user['study_id'])
    try:
        uploaded_file = decrypt_device_file(patient_id, uploaded_file, client_private_key )
    except (DecryptionKeyError, HandledError) as e:
        # when decrypting fails, regardless of why, we rely on the decryption code
        # to log it correctly and return 200 OK to get the device to delete the file.
        # We do not want emails on these types of errors, so we use log_error explicitly.
        print "the following error was handled:"
        log_error(e, "%s; %s; %s" % (patient_id, file_name, e.message) )
        return render_template('blank.html'), 200

    #print "decryption success:", file_name
    #if uploaded data a) actually exists, B) is validly named and typed...
    if uploaded_file and file_name and contains_valid_extension( file_name ):
        s3_upload( file_name.replace("_", "/") , uploaded_file, user["study_id"] )
        FileToProcess.append_file_for_processing(file_name.replace("_", "/"), user["study_id"], patient_id)
        return render_template('blank.html'), 200
    
    else:
        error_message ="an upload has failed " + patient_id + ", " + file_name + ", "
        if not uploaded_file:
            #it appears that very occasionally the app creates some spurious files 
            #with a name like "rList-org.beiwe.app.LoadingActivity"
            error_message += "there was no/an empty file, returning 200 OK so device deletes bad file."
            log_error( Exception("upload error"), error_message )
            return render_template('blank.html'), 200
        
        elif not file_name:
            error_message += "there was no provided file name, this is an app error."
        elif file_name and not contains_valid_extension( file_name ):
            error_message += "contains an invalid extension, it was interpretted as "
            error_message += grab_file_extension(file_name)
        else: error_message += "AN UNKNOWN ERROR OCCURRED."
        log_and_email_error( Exception("upload error"), error_message )
        return abort(400)


################################################################################
############################## Registration ####################################
################################################################################

@mobile_api.route('/register_user', methods=['GET', 'POST'])
@authenticate_user_registration
def register_user():
    """ Checks that the patient id has been granted, and that there is no device
        registered with that id.  If the patient id has no device registered it
        registers this device and logs the bluetooth mac address.

        Check the documentation in user_authentication to ensure you have provided
        the proper credentials.

        Returns the encryption key for this patient/user. """

    #CASE: If the id and password combination do not match, the decorator returns a 403 error.
    #the following parameter values are required.
    patient_id = request.values['patient_id']
    phone_number = request.values['phone_number']
    device_id = request.values['device_id']

    #These values may not be returned by earlier versions of the beiwe app
    try: device_os = request.values['device_os']
    except BadRequestKeyError: device_os = "none"
    try: os_version = request.values['os_version']
    except BadRequestKeyError: os_version = "none"
    try: product = request.values["product"]
    except BadRequestKeyError: product = "none"
    try: brand = request.values["brand"]
    except BadRequestKeyError: brand = "none"
    try: hardware_id = request.values["hardware_id"]
    except BadRequestKeyError: hardware_id = "none"
    try: manufacturer = request.values["manufacturer"]
    except BadRequestKeyError: manufacturer = "none"
    try: model = request.values["model"]
    except BadRequestKeyError: model = "none"
    try: beiwe_version = request.values["beiwe_version"]
    except BadRequestKeyError: beiwe_version = "none"
    #This value may not be returned by later versions of the beiwe app.
    try: mac_address = request.values['bluetooth_id']
    except BadRequestKeyError: mac_address = "none"

    user = User(patient_id)
    study_id = user['study_id']

    if brand.lower() == "apple":
        #TODO: implement ios-specific logic. (possibly a diffirent function entirely?)
        pass

    if user['device_id'] is not None and user['device_id'] != request.values['device_id']:
        # CASE: this patient has a registered a device already and it does not
        # match this device.  They need to contact the study and unregister
        # their their other device.  The device will receive a 405 error and
        # should alert the user accordingly.
        # Provided a user does not completely reset their device (which resets
        # the device's unique identifier) they user CAN reregister an existing
        # device, the unlock key they need to enter to at registration is their\
        # old password.
        return abort(405)
    
    # At this point the device has been checked for validity and will be
    # registered successfully.  Any errors after this point will be server errors
    # and return 500 codes
    # the final return will be the encryption key associated with this user.
    
    #Upload the user's various identifiers.
    unix_time = str(calendar.timegm(time.gmtime() ) )
    file_name = patient_id + '/identifiers_' + unix_time + ".csv"
    #construct a manual csv of the device attributes
    header = "patient_id,MAC,phone_number,device_id,device_os,os_version,product,brand,hardware_id,manufacturer,model,beiwe_version\n"
    file_contents = (header + "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %
                     (patient_id, mac_address, phone_number, device_id, device_os,
                      os_version, product, brand, hardware_id, manufacturer, model,
                      beiwe_version) )
    # print file_contents, "\n"
    s3_upload( file_name, file_contents, study_id )
    FileToProcess.append_file_for_processing(file_name,
                                             user['study_id'],
                                             patient_id)

    # set up device.
    user.set_device( device_id )
    User(patient_id).set_password(request.values['new_password'])
    device_settings = Study(study_id).get_study_device_settings()
    device_settings.pop('_id', None)
    return_obj = {'client_public_key': get_client_public_key_string(patient_id, study_id),
                  'device_settings': device_settings}
    return json.dumps(return_obj), 200


################################################################################
############################### USER FUNCTIONS #################################
################################################################################

@mobile_api.route('/set_password', methods=['GET', 'POST'])
@authenticate_user
def set_password():
    """ After authenticating a user, sets the new password and returns 200.
    Provide the new password in a parameter named "new_password"."""
    User(request.values["patient_id"]).set_password(request.values["new_password"])
    return render_template('blank.html'), 200

################################################################################
########################## FILE NAME FUNCTIONALITY #############################
################################################################################

def grab_file_extension(file_name):
    """ grabs the chunk of text after the final period. """
    return file_name.rsplit('.', 1)[1]
    
def contains_valid_extension(file_name):
    """ Checks if string has a recognized file extension, this is not necessarily
        limited to 4 characters."""
    return '.' in file_name and grab_file_extension(file_name) in ALLOWED_EXTENSIONS

################################################################################
################################# Download #####################################
################################################################################

@mobile_api.route('/download_surveys', methods=['GET', 'POST'])
@authenticate_user
def get_latest_surveys():
    user = User(request.values['patient_id'])
    study = Study(user.study_id)
    return json.dumps(study.get_surveys_for_study())
