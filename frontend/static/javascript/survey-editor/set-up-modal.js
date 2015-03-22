/**
 * Code for setting up the Edit Question modal. Includes functions to pre-
 * populate the modal with a question's data, to clear the modal's fields for a
 * new question, and to display the appropriate input fields based on a
 * question's type.
 */

// When editing a question, populate the fields with that question's current attributes
function populateEditQuestionModal(question) {
    document.getElementById("text").value = question["question_text"];
    document.getElementById("type").value = question["question_type"];

    // Now that the question_type is selected, display the relevant fields
    removeAllAnswerOptionsRows();
    setQuestionType();

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

// Makes correct fields display in Edit Question modal, depending on the Question Type selected
function setQuestionType() {
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

// Resets the modal dialogue values to empty, used when creating a new question.
function clearModal() {
    // Loop sets all attributes of the modal dialogue to empty/default values
    var attrs = ["text","min","max","tfttxt","min_value", "max_value", "fields_div", "text_field_type"];
    for (var i = 0; i < attrs.length; i++) {
        if (i<=5) { document.getElementById(attrs[i]).value = ""; }
        if (i>5) { document.getElementById(attrs[i]).style.display = "none"; }
    }
    document.getElementById("type").value="info_text_box";
    document.getElementById("saveQuestion").onclick=addNewQuestion;

    clearInputFields();
    removeAllAnswerOptionsRows();
    setQuestionType();
}

// Loop through the <input> fields and set each one to an empty string
function clearInputFields() {
    var form = document.getElementById("questionForm");
    var inputs = form.getElementsByTagName("input");
    for (var index = 0; index < inputs.length; index++) {
        inputs[index].value = "";
    };
}
