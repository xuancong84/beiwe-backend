$(document).ready(function(){
    // Set up the main list of patients using DataTables
    $("#patients_list").DataTable();
});


function logout() {
    window.location.href="/logout";
}

function create_new_patient(study_id) {
    $.post('/create_new_patient/' + study_id, function(response) {
        alert("Created a new patient!\n" + response);
    });
    // TODO: reload page; try using location.reload() somewhere
}

function reset_device(patient_id) {
    $.post('/reset_device', { 'patient_id': patient_id }, function(response) {
        alert("For patient " + patient_id + ", " + response);
    });
    // TODO: reload page
}

function reset_patient_password(patient_id) {
    $.post('/reset_patient_password', { 'patient_id': patient_id }, function(response) {
        alert("Patient " + patient_id + "'s password has been reset to " + response);
    });
    // TODO: reload page
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