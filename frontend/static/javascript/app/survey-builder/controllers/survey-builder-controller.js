(function() {
  
  angular
    .module("surveyBuilder")
    .controller("SurveyBuilderCtrl", SurveyBuilderCtrl);
  
  function SurveyBuilderCtrl(
    QUESTION_FIELD_MAPPINGS,
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
    this.QUESTION_FIELD_MAPPINGS = QUESTION_FIELD_MAPPINGS;
    this.QUESTION_FIELDS_LIST = QUESTION_FIELDS_LIST;
    
    /* Load questions from window.questions, converted to frontend text */
    this.questions = (function() {
      return _.map(
        window.questions,
        function(value) {
          var convertedQuestion = {};
          _.each(
            value,
            function(value, key) {
              convertedQuestion[QUESTION_FIELD_MAPPINGS.toFrontend[key]] = value;
            }
          );
          return convertedQuestion;
        }
      );
    })();
    
    /* Current question for displaying/modifying with modal */
    this.currentQuestionFields = {
      "text": "",
      "type": QUESTION_TYPES.infoTextBox,
      "min": "",
      "max": "",
      "textFieldType": TEXT_FIELD_TYPES.numeric,
      "isNewQuestion": true,
      "index": null,
      "id": null,
      "answers": [{"text":"blah"}, {"text":"bloo"}]
    };
    this.defaultQuestionFields = angular.copy(this.currentQuestionFields);


    
    this.addAnswerField = function() {
      this.currentQuestionFields.answers.push({"text": ""});
    };
    this.deleteAnswerField = function(index) {
      this.currentQuestionFields.answers.splice(index, 1);
    };
    
    this.resetQuestionModal = function() {
      this.currentQuestionFields = angular.copy(this.defaultQuestionFields);
    };
    // Open the Edit Question modal, and pre-populate it with the data from the selected question
    this.launchEditQuestion = function(index) {
      this.resetQuestionModal();
      this.currentQuestionFields.isNewQuestion = false;
      this.currentQuestionFields.index = index;
    };
    // Get the question object from the Edit Question modal, and replace questions[index] with it
    this.editQuestion = function() {
      var questionType = this.currentQuestionFields.type;
      var questionObject = _.pickBy(
        this.currentQuestionFields,
        function(value, key) {
          var questionFields = QUESTION_FIELDS_LIST.frontend[questionType];
          return _.includes(questionFields, key);
        }
      );
      this.questions.splice(this.currentQuestionFields.index, 1, questionObject);
    }
  }
})();