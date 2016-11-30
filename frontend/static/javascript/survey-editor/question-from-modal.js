// Return a string that is the question's type
function getQuestionType() {
    var typeDropDown = document.getElementById("type");
    return typeDropDown.options[typeDropDown.selectedIndex].value;
}

// Return FALSE if the text_field_type drop-down/<select> is invisible; otherwise return a string
function getTextFieldType() {
    var typeDropDown = document.getElementById("tfttxt");
    if (typeDropDown === null || typeDropDown.offsetParent === null) { // If the <select> element is hidden
        return false;
    }
    else { // If the <select> element is not hidden
        return typeDropDown.options[typeDropDown.selectedIndex].value;
    }
}

// Generate a UUID; taken from Briguy37's post: http://stackoverflow.com/a/8809472
