$(document).ready(function(){
    // Set up the main list of patients using DataTables
    $("#patients_list").DataTable();
});


function logout() {
    window.location.href="/logout";
}

function create_new_patient() {
    $.post('/create_new_patient', function(response) {
        alert("Created a new patient!\n" + response);
    });
    // TODO: reload page
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
