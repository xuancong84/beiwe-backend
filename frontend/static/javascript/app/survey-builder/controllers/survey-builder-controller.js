(function() {
  
  angular
    .module("surveyBuilder")
    .controller("SurveyBuilderCtrl", SurveyBuilderCtrl);
  
  function SurveyBuilderCtrl(
    QUESTION_FIELDS_LIST,
    QUESTION_TYPE_LABELS,
    QUESTION_TYPES,
    TEXT_FIELD_TYPES,
    TEXT_FIELD_TYPE_LABELS
  ) {
    /* Constants for use in template */
    this.QUESTION_TYPES = QUESTION_TYPES;
    this.QUESTION_TYPE_LABELS = QUESTION_TYPE_LABELS;
    this.TEXT_FIELD_TYPES = TEXT_FIELD_TYPES;
    this.TEXT_FIELD_TYPE_LABELS = TEXT_FIELD_TYPE_LABELS;
    this.QUESTION_FIELDS_LIST = QUESTION_FIELDS_LIST;
    
    this.questions = window.questions;
    
    /* Current question for displaying/modifying with modal */
    this.currentQuestionFields = {
      "question_text": "",
      "question_type": QUESTION_TYPES.infoTextBox,
      "min": "",
      "max": "",
      "text_field_type": TEXT_FIELD_TYPES.numeric,
      "is_new_question": true,
      "index": null,
      "question_id": null,
      "answers": []
    };
    this.defaultQuestionFields = angular.copy(this.currentQuestionFields);

    this.addAnswerField = function() {
      this.currentQuestionFields.answers.push({"text": ""});
    };
    this.deleteAnswerField = function(index) {
      this.currentQuestionFields.answers.splice(index, 1);
    };
    
    this.resetQuestionModal = function(overrides) {
      /**
       * Resets the edit question modal to its default, overwriting the default with anything passed to overrides
       * Args:
       *   overrides (object): the question object to overwrite with
       */
      this.currentQuestionFields = angular.copy(this.defaultQuestionFields);
      _.extend(this.currentQuestionFields, overrides);
    };
    
    this.populateEditQuestionModal = function(index) {
      this.resetQuestionModal(this.questions[index]);
      this.currentQuestionFields.is_new_question = false;
      this.currentQuestionFields.index = index;
    };
    // Get the question object from the Edit Question modal, and replace questions[index] with it
    this.editQuestion = function() {
      var questionType = this.currentQuestionFields.question_type;
      var questionObject = _.pick(this.currentQuestionFields, QUESTION_FIELDS_LIST[questionType]);
      this.questions.splice(this.currentQuestionFields.index, 1, questionObject);
    }
  }
})();