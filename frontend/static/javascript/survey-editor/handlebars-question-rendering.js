/**
 * Handlebars.js code to display Question Type and Options Array as Strings, etc.
 */

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
