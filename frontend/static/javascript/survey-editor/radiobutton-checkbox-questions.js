/**
 * Functionality for Radio Button and Checkbox questions that have variable
 * numbers of answers
 * Mostly adding and removing <input> (text-input) fields/boxes to and from the
 * array of possible answer choices associated with a question
 */

// Remove all <input> fields that can hold answer options
function removeAllAnswerOptionsRows() {
    var optionsRows = document.getElementsByName("optionsRow");
    optionsRowsCount = optionsRows.length
    for (var i = 0; i < optionsRowsCount; i++) {
        /* For every iteration, optionsRows gets recreated as a 1-smaller
        array, so keep deleting the first element */
        optionsRows[0].parentNode.removeChild(optionsRows[0]);
    };
}

// Add a new <input> field to the bottom of the list of answer options
function addField() {
    var fieldsRow = document.getElementById('fields_div');
    var newFieldRow = document.createElement("tr");
    newFieldRow.setAttribute('name', 'optionsRow');
    newFieldRow.innerHTML = '<td></td><td><input type="text" name="option"></input></td><td><button type="button" onclick="deleteField(this)">Delete</button></td>';
    fieldsRow.appendChild(newFieldRow);
}

// Delete a row with an <input> field in it
function deleteField(elem) {
    elem.parentNode.parentNode.remove();
}
