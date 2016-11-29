angular.module("surveyBuilder")
  .constant("QUESTION_TYPES", {
    "infoTextBox": "info_text_box",
    "slider": "slider",
    "radio": "radio_button",
    "checkbox": "checkbox"
  })
  .service("QUESTION_TYPE_LABELS", function(QUESTION_TYPES) {
    this[QUESTION_TYPES.infoTextBox] = "Informational Text";
    this[QUESTION_TYPES.slider] = "Slider";
    this[QUESTION_TYPES.radio] = "Radio Button";
    this[QUESTION_TYPES.checkbox] = "Checkbox";
    this[QUESTION_TYPES.freeResponse] = "Free Response";
  })
  .constant("TFTTXT_TYPES", {
    "numeric": "NUMERIC",
    "singleLine": "SINGLE_LINE_TEXT",
    "multiLine": "MULTI_LINE_TEXT"
  })
  .service("TFTTXT_TYPE_LABELS", function(TFTTXT_TYPES) {
    this[TFTTXT_TYPES.numeric] = "Numeric";
    this[TFTTXT_TYPES.singleLine] = "Single-line Text";
    this[TFTTXT_TYPES.multiLine] = "Multi-line Text";
  });
