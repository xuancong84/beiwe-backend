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

// Loop through the <input> fields and set each one to an empty string
function clearInputFields() {
    var form = document.getElementById("questionForm");
    var inputs = form.getElementsByTagName("input");
    for (var index = 0; index < inputs.length; index++) {
        inputs[index].value = "";
    };
}
