$(document).ready(function(){
    // Set up the main list of patients using DataTables
    $("#patients_list").DataTable();

    $('#many-new-patients-loading-spinner').hide();

    $('#createManyPatientsForm').on('submit', function(e){
        $('#createManyPatientsButton').prop('disabled', true);  // Disable the button so they can't click it twice
        $('#many-new-patients-loading-spinner').show();
        $('#many-new-patients-submit-and-cancel-buttons').hide();
    });

    $('#addManyPatientsModal').on("hidden.bs.modal", function() {
        location.reload();
    });
});

function logout() {
    window.location.href="/logout";
}

function create_new_patient(study_id) {
    $('.add_new_patient_button').prop('disabled', true);  // Disable the button so they can't click it twice
    $.ajax({
        type: 'POST',
        url: '/create_new_patient/' + study_id,
        data: {
        },
        statusCode: {
            201: function(response) {
                alert("Created a new patient:\n" + response);
            }
        }
    }).done(function() {
        location.reload();
    }).fail(function() {
        alert("Something went wrong when trying to create a new patient, sorry!");
        $('#add_new_patient_button').prop('disabled', false);  // Re-enable the button
    });
}

function reset_device(study_id, patient_id) {
    $('.reset_device_button').prop('disabled', true);  // Disable all reset_device buttons
    $.ajax({
        type: 'POST',
        url: '/reset_device/' + study_id,
        data: {
            'patient_id': patient_id
        },
        statusCode: {
            201: function(response) {
                alert("For patient " + patient_id + ", " + response);
            }
        }
    }).done(function() {
        location.reload();
    }).fail(function() {
        alert("Sorry, something went wrong when trying to reset the patient's device.");
        $('.reset_device_button').prop('disabled', false);  // Re-enable all reset_device buttons
    });
}

function reset_patient_password(study_id, patient_id) {
    $('.reset_password_button').prop('disabled', true);  // Disable all reset_password buttons
    $.ajax({
        type: 'POST',
        url: '/reset_patient_password/' + study_id,
        data: {
            'patient_id': patient_id
        },
        statusCode: {
            201: function(response) {
                alert("Patient " + patient_id + "'s password has been reset to " + response);
            }
        }
    }).done(function() {
        // No need to reload the page, since no visible change is displayed
        $('.reset_password_button').prop('disabled', false);  // Re-enable all reset_password buttons
    }).fail(function() {
        alert("Sorry, something went wrong when trying to reset the patient's password.");
        $('.reset_password_button').prop('disabled', false);  // Re-enable all reset_password buttons
    });
}

function remove_admin_from_study(admin_id, study_id) {
    $('.add_admin_to_study_button').prop('disabled', true);  // Disable the button
    $.ajax({
        type: 'POST',
        url: '/remove_admin_from_study',
        data: {
            admin_id: admin_id,
            study_id: study_id
        }
    }).done(function() {
        location.reload();
    }).fail(function() {
        alert("There was a problem with removing the admin, sorry!");
        $('.add_admin_to_study_button').prop('disabled', false);  // Re-enable the button
    });
}

function add_admin_to_study() {
    $('.remove_admin_from_study_button').prop('disabled', true);  // Disable the link
    $.ajax({
        type: 'POST',
        url: '/add_admin_to_study',
        data: {
            admin_id: $('#admin_id').val(),
            study_id: $('#study_id').val()
        }
    }).done(function() {
        location.reload();
    }).fail(function() {
        alert("There was a problem with adding the admin, sorry!");
        $('.remove_admin_from_study_button').prop('disabled', false);  // Re-enable the link
    });
}

/* Pop up a confirmation dialog and only delete the study if the user types an EXACT string */
function confirm_delete_study(study_name, study_id) {
    var required_matching_text = "Yes, I want to delete " + study_name;
    var prompt_message = "Are you ABSOLUTELY SURE that you want to delete the study " + study_name +" and all users and surveys associated with it?\nIf you're DEAD CERTAIN, type '" + required_matching_text + "' in the box here:";
    var confirmation_prompt = prompt(prompt_message);
    if (confirmation_prompt == required_matching_text) {
        $.ajax({
            type: 'POST',
            url: '/delete_study/' + study_id,
            data: {
                confirmation: "true"
            }
        }).done(function() {
            location.href = "/manage_studies";
        }).fail(function() {
            alert("There was a problem with deleting the study.");
        });
    };
}
