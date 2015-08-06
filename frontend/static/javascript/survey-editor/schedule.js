var days_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function renderSchedule() {
    var source = $("#schedule-template").html();
    var template = Handlebars.compile(source);

    survey_times = [[2, 3, 5], [6, 9, 15], [5, 4], [2], [4], [4], [19]];

    var schedule = [];
    for (var i=0; i<7; i++) {
    	day_schedule = {day_name: days_list[i], times: survey_times[i]};
    	schedule.push(day_schedule);
    };

//console.log(schedule);
    var dataList = {schedules: schedule};
//    var dataList = { times: survey_times, day_names: days_list };
//    var dataList = { times: [{time: 2}, {time: 3}, {time: 4}] };
    var htmlSchedule = template(dataList);

    $('#surveySchedule').html(htmlSchedule);
}
