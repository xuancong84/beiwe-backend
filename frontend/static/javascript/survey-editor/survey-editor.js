/**
 * Functionality to create and edit surveys via a web form
 */

var questions = [];

$(document).ready(function() {

    // Determine if it's a daily or weekly survey
    var surveyType = document.getElementById("surveyType").title;

    // Get the correct URL to pull the current copy of the daily or weekly survey
    var current_survey_url = "https://beiwe.org/get_daily_survey";
    if (surveyType.localeCompare("weekly") == 0) {
        current_survey_url = "https://beiwe.org/get_weekly_survey";
    }

    // Get the current survey's JSON, and render it as a list of questions
    $.getJSON(current_survey_url, function(data) {
        questions = data["questions"];
        renderQuestionsList();
        displayScheduledTime(data["hour_of_day"], data["day_of_week"]);
    })
});

// Return the hour number (in 24-hour time) that the user selected in the form
function getHour() {
    var hour = parseInt(document.getElementById("hour").value);
    var ampm = document.getElementById("ampm").value;
    if (hour == 12) {
        hour = 0; // 12a.m. is really 0:00; 12p.m. is really 12:00
    }
    if (ampm.localeCompare("pm") == 0) {
        hour += 12; // If time is p.m., add 12 to the hour
    };
    return hour;
}

// If it's a weekly survey, return the selected weekday (Sunday = 1, Saturday = 7)
function getDayOfWeek() {
    var dayPicker = document.getElementById("day");
    if (dayPicker === 'undefined' || dayPicker == null) {
        return null;
    }
    return parseInt(dayPicker.value);
}

// On end(), export the survey as a JSON object
function end() {
    // Send a POST request (using XMLHttpRequest) with the JSON survey object as a parameter
    var postRequestContent = "JSONstring=" + JSON.stringify(createJsonSurveyObject());
    var xhr = new XMLHttpRequest();
    // If you're editing the weekly survey, update the weekly survey
    var surveyType = document.getElementById("surveyType").title;
    if (surveyType.localeCompare("weekly") == 0) {
        xhr.open("POST", "https://beiwe.org/update_weekly_survey", true);
    }
    // Otherwise, you're editing the daily survey
    else {
        xhr.open("POST", "https://beiwe.org/update_daily_survey", true);
    }
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    xhr.send(postRequestContent);
    alert("Survey results sent successfully :)")
}

// Turn the survey into a JSON object with an array of questions and other attributes
function createJsonSurveyObject() {
    var survey_id_string;
    var surveyType = document.getElementById("surveyType").title;
    if (surveyType.localeCompare("weekly") == 0) {
        survey_id_string = "WeeklySurveyCreatedAt" + new Date().getTime();
    }
    else {
        survey_id_string = "DailySurveyCreatedAt" + new Date().getTime();
    }
    var surveyObject = {
        hour_of_day: getHour(),
        questions: questions,
        survey_id: survey_id_string
    }
    // If it's a weekly survey, add the day of the week to ask the survey
    if (getDayOfWeek() != null) {
        surveyObject.day_of_week = getDayOfWeek();
    }
    return surveyObject;
}

// Render a list of the current questions
function renderQuestionsList() {
    // Get the question template, and compile it using Handlebars.js
    var source = $("#question-template").html();
    var template = Handlebars.compile(source);

    // Use the list of questions as the data list to populate the template
    var dataList = { questions: questions };
    var htmlQuestion = template(dataList);

    // Insert the template into the page's HTML
    $("#listOfCurrentQuestions").html(htmlQuestion);
}

// Display the survey's scheduled time in the drop-down menus at the top
function displayScheduledTime(hour, day) {
    // Translate 24-hr time to 12-hr time with a.m./p.m. labels
    if (hour >= 12) {
        document.getElementById("ampm").value = "pm";
        hour -= 12;
    }
    else {
        document.getElementById("ampm").value = "am";
    }
    // Translate 0:00 to 12:00am, and 12:00 to 12:00pm
    if (hour == 0) {
        hour = 12;
    }
    // Set the Hour and Day HTML <select> drop-downs
    document.getElementById("hour").value = hour;
    document.getElementById("day").value = day;
}

// Get the question object from the Edit Question modal, and append it to the questions array
function addNewQuestion() {
    var questionObject = getQuestionObjectFromModal();
    questions.push(questionObject);
    renderQuestionsList();
}

// Get the question object from the Edit Question modal, and replace questions[index] with it
function replaceQuestion(index) {
    var questionObject = getQuestionObjectFromModal();
    questions.splice(index, 1, questionObject);
    renderQuestionsList();
}

// Open the Edit Question modal, and pre-populate it with the data from the selected question
function editQuestion(index) {
    clearModal();
    populateEditQuestionModal(questions[index]);
    document.getElementById("saveQuestion").onclick = function() { replaceQuestion(index); };
}

// Remove the selected question from the questions array, and re-render the HTML list of questions
function deleteQuestion(index) {
    questions.splice(index, 1);
    renderQuestionsList();
}

// Swap the question with the one before it, as long as it's not the first in the list
function moveQuestionUp(index) {
    if (index > 0) {
        questions.splice(index - 1, 2, questions[index], questions[index - 1]);
        renderQuestionsList();
    };
}

// Swap the question with the one after it, as long as it's not the last in the list
function moveQuestionDown(index) {
    if (index < questions.length - 1) {
        questions.splice(index, 2, questions[index + 1], questions[index]);
        renderQuestionsList();
    };
}
