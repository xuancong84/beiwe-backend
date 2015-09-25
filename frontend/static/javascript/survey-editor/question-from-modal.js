/**
 * Get a question object from the fields in the Edit Question modal
 */

// Return an object that is a question and can be JSON-ified
function getQuestionObjectFromModal() {
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
            sanitized_input_value = input.value.replace(/"/g, "\u201C");
            if (input.name.localeCompare("option") == 0) {
                optionsArray.push({"text": sanitized_input_value});
            }
            else {
                questionObject[input.name] = sanitized_input_value;
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