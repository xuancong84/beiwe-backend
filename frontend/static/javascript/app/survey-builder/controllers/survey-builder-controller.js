(function() {  
  function SurveyBuilderCtrl(QUESTION_TYPES, QUESTION_TYPE_LABELS, TFTTXT_TYPES, TFTTXT_TYPE_LABELS) {
    /* Add Question modal */
    this.currentQuestionFields = {
      "questionText": "",
      "questionType": QUESTION_TYPES.infoTextBox,
      "questionMin": "",
      "questionMax": "",
      "tfttxt": TFTTXT_TYPES.numeric,
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