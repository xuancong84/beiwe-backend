/**
 * Functionality to create and edit surveys via a web form
 */

var questions = [];

// When the page loads, get the current JSON survey and load the questions[] array from it
$.getJSON("http://beiwe.org/fetch_survey", function(data) {
    questions = data["questions"];
    renderQuestionsList();
})

// On end(), export the survey as a JSON object
function end() {
    var timestamp = new Date().getTime();
    var surveyObject = {
        questions: questions,
        survey_id: "SurveyCreatedAt" + timestamp
    }
    //TODO: Josh.  Implement a check for pushing to daily and pushing to weekly.
    // Send a POST request (using XMLHttpRequest) with the JSON survey object as a parameter
    var postRequestContent = "JSONstring=" + JSON.stringify(surveyObject);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://beiwe.org/update_survey", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
    xhr.send(postRequestContent);
    alert("Survey results sent successfully :)")
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
