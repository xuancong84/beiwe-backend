var questions = [];

window.onload = function setupEverything() {
}

// When the page loads, get the current JSON survey and load the questions[] array from it
$.getJSON("http://beiwe.org/fetch_survey", function(data) {
    questions = data["questions"];
    renderQuestionsList();
})

function exportSurvey() {
    var surveyObject = {
        questions:questions,
        survey_id:"42" // TODO: create a sequential survey ID (maybe a UNIX timestamp)
    }

    console.log(JSON.stringify(surveyObject));
}


/*###########################################################################
###################   Question-rendering functionality  #####################
###########################################################################*/

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

// Return a human-readable string instead of a variable name
Handlebars.registerHelper("questionTypeTextString", function(inString) {
    switch (inString) {
        case "info_text_box": return "Info Text Box";
        case "slider": return "Slider";
        case "radio_button": return "Radio Button";
        case "checkbox": return "Checkbox";
        case "free_response": return "Free Response";
        default: return "Question type error";
    }
});

// Return the list of answer options (for Radio Button/ Checkbox questions) as a single string
Handlebars.registerHelper("optionsArrayToString", function(optionsArray) {
    var optionsString = "";
    for (var i = 0; i < optionsArray.length; i++) {
        optionsString += optionsArray[i]["text"] + ", ";
    };
    return optionsString;
});


/*###########################################################################
#########   Edit Question pop-up-to-JSON functionality  #####################
###########################################################################*/

// Get the question object from the Edit Question modal, and append it to the questions array
function addNewQuestion() {
    var questionObject = getQuestionObject();
    questions.push(questionObject);
    renderQuestionsList();
}

// Get the question object from the Edit Question modal, and replace questions[index] with it
function replaceQuestion(index) {
    var questionObject = getQuestionObject();
    questions.splice(index, 1, questionObject);
    renderQuestionsList();
}

// When editing a question, populate the fields with that question's current attributes
function populateEditQuestionModal(question) {
    document.getElementById("text").value = question["question_text"];
    document.getElementById("type").value = question["question_type"];

    // Now that the question_type is selected, display the relevant fields
    removeAllAnswerOptionsRows();
    setType();

    // If it's a Radio Button or Checkbox question, render and populate the answer option fields
    var optionsArray = question["answers"];
    if (!(typeof optionsArray === 'undefined')) {
        for (var i = 0; i < optionsArray.length; i++) {
            addField();
            var optionsFields = document.getElementsByName("option");
            optionsFields[optionsFields.length - 1].value = optionsArray[i]["text"];
        };
    };

    // Show the other fields if they have values (min and max for Slider questions; etc.)
    document.getElementById("min").value = question["min"];
    document.getElementById("max").value = question["max"];
    document.getElementById("tfttxt").value = question["text_field_type"];
}

// Return an object that is a question and can be JSON-ified
function getQuestionObject() {
    // TODO: somehow generate a question ID number/string

    // Create a question object, and add to it the question_type attribute
    var questionObject = {
        question_type: getQuestionType()
    };

    // Create an empty Answer Options array, if it's a Radio Button or Free Response question
    var optionsArray = [];

    // Loop through all the visible inputs in the editQuestion pop-up/modal form
    var form = document.getElementById("questionForm");
    var inputs = form.getElementsByTagName("input");
    for (var index = 0; index < inputs.length; index++) {
        var input = inputs[index];
        if (input.offsetParent !== null) {  // If the <input> element is not hidden
            /* Add a key-value pair to the questionObject, using the <input> element's "name"
            attribute as the key, and the <input>'s value as it's value */
            if (input.name.localeCompare("option") == 0) {
                optionsArray.push({"text": input.value});
            }
            else {
                questionObject[input.name] = input.value;
            };
        }
    };

    // If it's a Radio Button or Checkbox question, there should be an array of answer options
    if (optionsArray.length > 0) {
        questionObject["answers"] = optionsArray;
    };

    // If it's a Free Response question, set the variable text_field_type from the drop-down menu
    if (getTextFieldType()) {
        questionObject["text_field_type"] = getTextFieldType();
    };

    // Add a question ID string
    questionObject["question_id"] = generateUUID();

    return questionObject;
}

// Return a string that is the question's type
function getQuestionType() {
    var typeDropDown = document.getElementById("type");
    return typeDropDown.options[typeDropDown.selectedIndex].value;
}

// Return FALSE if the text_field_type drop-down/<select> is invisible; otherwise return a string
function getTextFieldType() {
    var typeDropDown = document.getElementById("tfttxt");
    if (typeDropDown.offsetParent === null) { // If the <select> element is hidden
        return false;
    }
    else { // If the <select> element is not hidden
        return typeDropDown.options[typeDropDown.selectedIndex].value;
    }
}

// Generate a UUID; taken from Briguy37's post: http://stackoverflow.com/a/8809472
function generateUUID(){
    var d = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x7|0x8)).toString(16);
    });
    return uuid;
};

/*###########################################################################
################################   Other functionality  #####################
###########################################################################*/

// Makes correct fields display in Edit Question modal, depending on the Question Type selected
function setType() {
    var questionType = document.getElementById("type").value;

    // Set everything to invisible
    document.getElementById("min_value").style.display = "none";
    document.getElementById("max_value").style.display = "none";
    document.getElementById("fields_div").style.display = "none";
    document.getElementById("text_field_type").style.display = "none";

    // Make certain fields visible based on which questionType is selected
    switch(questionType) {
        case "info_text_box":
            break;
        case "slider":
            document.getElementById("min_value").style.display = "table-row";
            document.getElementById("max_value").style.display = "table-row";
            break;
        case "radio_button":
            document.getElementById("fields_div").style.display = "table-row-group";
            break;
        case "checkbox":
            document.getElementById("fields_div").style.display = "table-row-group";
            break;
        case "free_response":
            document.getElementById("text_field_type").style.display = "table-row";
            document.getElementById("tfttxt").value = "NUMERIC"; // Set it to a default value
            break;
    }
}

function removeAllAnswerOptionsRows() {
    var optionsRows = document.getElementsByName("optionsRow");
    optionsRowsCount = optionsRows.length
    for (var i = 0; i < optionsRowsCount; i++) {
        /* For every iteration, optionsRows gets recreated as a 1-smaller
        array, so keep deleting the first element */
        optionsRows[0].parentNode.removeChild(optionsRows[0]);
    };
}

function addField() {
    var fieldsRow = document.getElementById('fields_div');
    var newFieldRow = document.createElement("tr");
    newFieldRow.setAttribute('name', 'optionsRow');
    newFieldRow.innerHTML = '<td></td><td><input type="text" name="option"></input></td><td><button type="button" onclick="deleteField(this)">Delete</button></td>';
    fieldsRow.appendChild(newFieldRow);
}

function deleteField(elem) {
    elem.parentNode.parentNode.remove();
}

function clearModal() {
    console.log("clearModal() just got called");
    //resets the modal dialogue values to empty, used when creating a new question.
    /*loop sets all attributes of the modal dialogue to empty/default values.*/
    var attrs = ["text","min","max","tfttxt","min_value", "max_value", "fields_div", "text_field_type"];
    for (var i = 0; i < attrs.length; i++) {
        if (i<=5) { document.getElementById(attrs[i]).value = ""; }
        if (i>5) { document.getElementById(attrs[i]).style.display = "none"; }
    }
    document.getElementById("type").value="info_text_box";
    document.getElementById("saveQuestion").onclick=addNewQuestion;

    clearInputFields();
    removeAllAnswerOptionsRows();
}

// Loop through the <input> fields and set each one to an empty string
function clearInputFields() {
    var form = document.getElementById("questionForm");
    var inputs = form.getElementsByTagName("input");
    for (var index = 0; index < inputs.length; index++) {
        inputs[index].value = "";
    };
}

function setModal(question_name) {
    //TODO: only answerID is used more than once in the logic.
    //TODO: typeid is only ever used as part of document.getElementById(typeid).textContent
    console.log("setModal");
    document.getElementById("saveQuestion").onclick=changeQuestion;
    var nameid = question_name + 'name';
    document.getElementById("name").value = document.getElementById(nameid).textContent;
    var textid = question_name + 'text';
    document.getElementById("text").value = document.getElementById(textid).textContent;

    var rangeid = question_name + 'range';
    var typeid = question_name + 'type';
    var defaultid = question_name + 'default';
    var tftid = question_name + 'tft';
    var answersid = question_name + 'answers';

    document.getElementById("oldName").value = question_name;
    if (document.getElementById(typeid).textContent == "slider") {
        console.log("slider");
        document.getElementById("type").value = "2";
        document.getElementById("min").value = document.getElementById(rangeid).textContent;
        document.getElementById("max").value = document.getElementById(defaultid).textContent;
    } else if (document.getElementById(typeid).textContent == "radio_button") {
        console.log("radio");
         document.getElementById("type").value = "3";
    } else if (document.getElementById(typeid).textContent == "checkbox") {
        console.log("checkbox");
        document.getElementById("type").value = "4";
    } else if (document.getElementById(typeid).textContent == "free_response") {
        console.log("free");
        document.getElementById("type").value = "5";
        document.getElementById("tfttxt").value = document.getElementById(tftid).textContent;
    } else {
        console.log("info");
        document.getElementById("type").value = "1";
    }
}

function changeQuestion() {
    // Replaces the saved question with the contents of the working question.
    console.log("change");
    createQuestion();
    var x = document.question.oldName.value;
    deleteQuestion(x);
}

/*function deleteQuestion(x) {
    //TODO: track down exactly what x is, rename variable accordingly.
    // deletes a question.
    console.log("delete");
    var old = document.getElementById(x);
    old.parentNode.removeChild(old);
}*/

// shall henceforth be referred to as "The Monster"
function createQuestion() {
    var name = document.question.name.value;
    var html = '<div id="' + name + '" class="row">';
    html += '<h3 id="' + name + 'name">' + name + '</h3>';
    html += '<input type="text" style="display:none;" name="' + name + '" value="' + name + '"></input>';
    if (document.getElementById("type").value == '2') {
        html += 'Question type: <div id="' + name + 'type">slider</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += 'Slider range: <div id="' + name + 'range">' + document.question.min.value + '</div>';
        html += 'default: <div id="' + name + 'default">' + document.question.max.value + '</div>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="slider"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'range" value="' + document.question.min.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'default" value="' + document.question.max.value + '"></input>';
    } else if (document.getElementById("type").value == '3') {
        html += 'Question type: <div id="' + name + 'type">radio_button</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += 'Answers:';
        html += '<div id="' + name + 'answers">';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="radio_button"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
    } else if (document.getElementById("type").value == '4') {
        html += ' <div id="' + name + 'type">Question type:checkbox</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += 'Answers:';
        html += '<div id="' + name + 'answers">';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="checkbox"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
    } else if (document.getElementById("type").value == '5') {
        html += 'Question type: <div id="' + name + 'type">free_response</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += 'Text Field Type: <div id="' + name + 'tft">' + document.question.tfttxt.value + '</div>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="free_response"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'tft" value="' + document.question.tfttxt.value + '"></input>';
    } else {
        html += 'Question type: <div id="' + name + 'type">informational_text</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="informational_text"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
    }
    html += '<button class="btn btn-primary" data-toggle="modal" data-target="#editQuestionModal" onclick="setModal(\'' + name + '\'); return false;">Edit</button>';
    html += '<button class="btn btn-primary" onclick="deleteQuestion(\'' + name + '\'); return false;">Delete</button>';
    addHTML(html);
}


//Accourding to Mike, we are probably good as long as they are running something newer than i.e. 7
//TODO: put in a check somewhere about browser version.
function addHTML(html) {
    document.getElementById("newQuestions").insertAdjacentHTML('beforeEnd', html);
//from following the code flow, the first one (document.all) must be the one that passes on modern browsers, and then the document
//     if (document.all) { //document.all is a MS proprietary command, I believe this is code to handle IE.
//         document.getElementById("newQuestions").insertAdjacentHTML('beforeEnd', html);
//     }
//     else if (document.createRange) { //handles another case, only works in ie and Opera (but works on chris's firefox
//         var range = document.createRange();
//         range.setStartAfter(document.body.lastChild);
//         var cFrag = range.createContextualFragment(html);
//         document.getElementById("newQuestions").appendChild(cFrag);
//     }
//     else if (document.layers) { //and this is some old Netscape compatible javascript
//         var X = new Layer(window.innerWidth);
//         X.document.open();
//         X.document.write(html);
//         X.document.close();
//         X.top = document.height;
//         document.height += X.document.height;
//         X.visibility = 'show';
//     }
}


function end() {
    //TODO: work out the python command to pull this of the form submission,
    // I think json.dumps(request.files["survey"])).
    //old: var payload = JSON.stringify($('#survey').serializeArray());

    //this works
    /*var payload = JSON.stringify($( document.getElementsByName("survey") ).serializeArray());
    console.log(payload);
    $.post("/update_weekly", payload);*/

    exportSurvey();
}



function get_survey(){
    return document.getElementByName("survey");

}

