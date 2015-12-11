var users_by_study = {};


$(document).ready(function() {
	patients_dict = JSON.parse(users_by_study);

	/* Set up Date/Time pickers */
    $('#start_datetimepicker').datetimepicker();
    $('#end_datetimepicker').datetimepicker();

    /* When the Study dropdown changes, display the correct list of patients for that study */
	display_patients_for_study();
	$('#study_selector').change(display_patients_for_study);

	/* When the form gets submitted, reformat the DateTimes into ISO UTC format */
	$('#data_download_parameters_form').submit(format_datetimepickers);
});

function display_patients_for_study() {
	study_id = $('#study_selector').val();
	patients_list = patients_dict[study_id];

    var source = $("#patient_select_template").html();
    var template = Handlebars.compile(source);
    var dataList = {patients: patients_list};
    var patient_list = template(dataList);
    $('#patient_selector').html(patient_list);
};

function format_datetimepickers() {
	/* If they're empty, remove this value from the POST request */
	if (!$('#start_datetime').val()) {
		$('#start_datetime').attr('disabled', 'disabled');
	};
	if (!$('#end_datetime').val()) {
		$('#end_datetime').attr('disabled', 'disabled');
	};

	/* Format DateTime strings */
	$('#start_datetime').val(moment($('#start_datetime').val()).format('YYYY-MM-DDTHH:mm:ss'));
	$('#end_datetime').val(moment($('#end_datetime').val()).format('YYYY-MM-DDTHH:mm:ss'));
	return true;
};