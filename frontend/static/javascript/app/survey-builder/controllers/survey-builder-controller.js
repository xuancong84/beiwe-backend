(function() {  
  function SurveyBuilderCtrl() {
    /* Constants */
    this.QUESTION_TYPES = {
      "infoTextBox": "info_text_box",
      "slider": "slider",
      "radio": "radio_button",
      "checkbox": "checkbox",
      "freeResponse": "free_response"
    };
    this.QUESTION_TYPE_LABELS = {};
    this.QUESTION_TYPE_LABELS[this.QUESTION_TYPES.infoTextBox] = "Informational Text";
    this.QUESTION_TYPE_LABELS[this.QUESTION_TYPES.slider] = "Slider";
    this.QUESTION_TYPE_LABELS[this.QUESTION_TYPES.radio] = "Radio Button";
    this.QUESTION_TYPE_LABELS[this.QUESTION_TYPES.checkbox] = "Checkbox";
    this.QUESTION_TYPE_LABELS[this.QUESTION_TYPES.freeResponse] = "Free Response";
    this.TFTTXT_TYPES = {
      "numeric": "NUMERIC",
      "singleLine": "SINGLE_LINE_TEXT",
      "multiLine": "MULTI_LINE_TEXT"
    };
    this.TFTTXT_TYPE_LABELS = {};
    this.TFTTXT_TYPE_LABELS[this.TFTTXT_TYPES.numeric] = "Numeric";
    this.TFTTXT_TYPE_LABELS[this.TFTTXT_TYPES.singleLine] = "Single-line Text";
    this.TFTTXT_TYPE_LABELS[this.TFTTXT_TYPES.multiLine] = "Multi-line Text";
    
    /* Add Question modal */
    this.currentQuestionFields = {
      "questionText": "",
      "questionType": this.QUESTION_TYPES.infoTextBox,
      "questionMin": "",
      "questionMax": "",
      "tfttxt": this.TFTTXT_TYPES.numeric,
      "isNewQuestion": true
    };
    this.defaultQuestionFields = angular.copy(this.currentQuestionFields);
    this.currentQuestionIndex = null;

    this.questions = window.questions;
    
    this.resetQuestionModal = function() {
      this.currentQuestionFields = angular.copy(this.defaultQuestionFields);
    };
    // Open the Edit Question modal, and pre-populate it with the data from the selected question
    this.launchEditQuestion = function(index) {
      this.currentQuestionIndex = index;
      this.resetQuestionModal();
      this.currentQuestionFields.isNewQuestion = false;
      console.log(this);
      populateEditQuestionModal(questions[index]);
    };
    // Get the question object from the Edit Question modal, and replace questions[index] with it
    this.editQuestion = function() {
      var questionObject = getQuestionObjectFromModal();
      questions.splice(this.currentQuestionIndex, 1, questionObject);
      renderQuestionsList();
    }
  }
  
  angular
    .module("surveyBuilder")
    .controller("SurveyBuilderCtrl", SurveyBuilderCtrl)
})();