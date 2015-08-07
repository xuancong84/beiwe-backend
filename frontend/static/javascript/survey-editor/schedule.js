var days_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];


// Return the time as an h:MM AM/PM string instead of as a number of seconds past midnight
Handlebars.registerHelper("int_to_time", function(number_of_seconds) {
    var time_string = "";

    // Add hours (in 12-hour time)
    time_string += Math.round(number_of_seconds / 3600) % 12 + ":";

    // Add minutes
    var minutes = Math.round((number_of_seconds % 3600) / 60);
    if (minutes < 10) {
        time_string += "0" + minutes;
    } else {
        time_string += minutes;
    };

    // Add AM/PM
    if (number_of_seconds < 3600 * 12) {
        time_string += " AM";
    } else {
        time_string += " PM";
    };

    return time_string;
});


function renderSchedule() {
    var source = $("#schedule-template").html();
    var template = Handlebars.compile(source);

    var schedule = [];
    for (var i=0; i<7; i++) {
    	day_schedule = {day_name: days_list[i], times: survey_times[i]};
    	schedule.push(day_schedule);
    };

    var dataList = {schedules: schedule};
    var htmlSchedule = template(dataList);

    $('#surveySchedule').html(htmlSchedule);
}