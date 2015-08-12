/**
 * Functionality to create and edit surveys via a web form
 */

var questions = [];

$(document).ready(function() {
    questions = JSON.parse(survey_content);
    renderQuestionsList();
    renderSchedule();

    $('.schedule-timepicker').timepicker();
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

// TODO: Josh, make this update the survey properly
// On end(), export the survey as a JSON object
function end() {
    // Send a POST request (using XMLHttpRequest) with the JSON survey object as a parameter
    $.ajax({
        type: 'POST',
        url: '/update_survey/' + survey_id,
        data: {
            questions: JSON.stringify(questions),
            timings: JSON.stringify(survey_times)
        },
        statusCode: {
            200: function(response) {
                // A redirect to the Login page will show up as a 200 redirect
                alert("Your session may have expired. Open a new browser tab, log in to beiwe.org, and then click the 'Save and Deploy' button again on this tab.");
            },
            201: function(response) {
                alert("Survey saved and submitted successfully!");
                location.reload();
            }
        }
    }).done(function() {
        // Don't do anything; this actually gets called BEFORE the statusCode functions
    }).fail(function() {
        alert("There was a problem with updating the survey, sorry!");
    })
}

// Turn the survey into a JSON object with an array of questions and other attributes
function createJsonSurveyObject() {
    var survey_id_string;
    survey_id_string = "WeeklySurveyCreatedAt" + new Date().getTime();
    var surveyObject = {
        hour_of_day: getHour(),
        questions: questions,
        survey_id: survey_id_string
    }
    // If it's a weekly survey, add the day of the week to ask the survey
    if (getDayOfWeek() != null) {
        surveyObject.day_of_week = getDayOfWeek();
    }
    console.log("surveyObject = ");
    console.log(surveyObject);
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
