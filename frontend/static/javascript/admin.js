$(document).ready(function(){
    // Set up the main list of patients using DataTables
    $("#patients_list").DataTable();
});


function logout() {
    window.location.href="/logout";
}

function create_new_patient(study_id) {
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
    })
}

function reset_device(patient_id) {
    $.ajax({
        type: 'POST',
        url: '/reset_device',
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
    })
}

function reset_patient_password(patient_id) {
    $.ajax({
        type: 'POST',
        url: '/reset_patient_password',
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
    }).fail(function() {
        alert("Sorry, something went wrong when trying to reset the patient's password.");
    })
}

function remove_admin_from_study(admin_id, study_id) {
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
    })
}

function add_admin_to_study() {
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
    })
}