angular.module("surveyBuilder")
  .constant("QUESTION_FIELD_MAPPINGS", (function() {
    /**
     * For converting question fields from what's expected backend (python) to what's expected frontend (javascript)
     * and vice-versa.
     */
    var backendToFrontend = {
      "question_type": "type",
      "question_text": "text",
      "min": "min",
      "max": "max",
      "answers": "answers",
      "text_field_type": "textFieldType",
      "question_id": "id"
    };
    var frontendToBackend = _.invert(backendToFrontend);
    return {
      "toFrontend": backendToFrontend,
      "toBackend": frontendToBackend
    }
  })())
  .constant("QUESTION_TYPES", {
    "infoTextBox": "info_text_box",
    "slider": "slider",
    "radio": "radio_button",
    "checkbox": "checkbox",
    "freeResponse": "free_response"
  })
  // We use .service() here instead of .constant() since you can't inject into .constant(). Behavior emulates the same
  // behavior as a .constant(); http://stackoverflow.com/a/23544466
  .service("QUESTION_TYPE_LABELS", function(QUESTION_TYPES) {
    this[QUESTION_TYPES.infoTextBox] = "Informational Text";
    this[QUESTION_TYPES.slider] = "Slider";
    this[QUESTION_TYPES.radio] = "Radio Button";
    this[QUESTION_TYPES.checkbox] = "Checkbox";
    this[QUESTION_TYPES.freeResponse] = "Free Response";
  })
  .service("QUESTION_FIELDS_LIST", function(QUESTION_TYPES, QUESTION_FIELD_MAPPINGS) {
    /**
     * A list of the keys necessary for each question type
     */
    var commonKeysFrontend = ["question_id", "question_text", "question_type"];
    this.backend = {};
    this.backend[QUESTION_TYPES.infoTextBox] = commonKeysFrontend;
    this.backend[QUESTION_TYPES.slider] = commonKeysFrontend.concat(["max", "min"]);
    this.backend[QUESTION_TYPES.radio] = commonKeysFrontend.concat(["answers"]);
    this.backend[QUESTION_TYPES.checkbox] = commonKeysFrontend.concat(["answers"]);
    this.backend[QUESTION_TYPES.freeResponse] = commonKeysFrontend.concat(["text_field_type"]);
    this.frontend = _.mapValues(
      this.backend, 
      function(value) {
        return _.map(value, function(value) { return QUESTION_FIELD_MAPPINGS.toFrontend[value]; })
      }
    )
  })
  .constant("TEXT_FIELD_TYPES", {
    "numeric": "NUMERIC",
    "singleLine": "SINGLE_LINE_TEXT",
    "multiLine": "MULTI_LINE_TEXT"
  })
  .service("TEXT_FIELD_TYPE_LABELS", function(TEXT_FIELD_TYPES) {
    this[TEXT_FIELD_TYPES.numeric] = "Numeric";
    this[TEXT_FIELD_TYPES.singleLine] = "Single-line Text";
    this[TEXT_FIELD_TYPES.multiLine] = "Multi-line Text";
  });
