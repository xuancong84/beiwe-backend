function logout() {
    window.location.href="/logout";
}

function create_new_patient() {
    $.post('http://beiwe.org/create_new_patient', function(response) {
        alert("Created a new patient!\n" + response);
    });
}
