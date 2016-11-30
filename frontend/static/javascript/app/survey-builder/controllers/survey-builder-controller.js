(function() {
  
  angular
    .module("surveyBuilder")
    .controller("SurveyBuilderCtrl", SurveyBuilderCtrl);
  
  function SurveyBuilderCtrl(QUESTION_FIELDS_LIST, QUESTION_TYPE_LABELS, QUESTION_TYPES,
                             TEXT_FIELD_TYPES, TEXT_FIELD_TYPE_LABELS, uuid) {
    /* Constants for use in template */
    this.QUESTION_TYPES = QUESTION_TYPES;
    this.QUESTION_TYPE_LABELS = QUESTION_TYPE_LABELS;
    this.TEXT_FIELD_TYPES = TEXT_FIELD_TYPES;
    this.TEXT_FIELD_TYPE_LABELS = TEXT_FIELD_TYPE_LABELS;
    this.QUESTION_FIELDS_LIST = QUESTION_FIELDS_LIST;
    
    /* Array of questions for this survey */
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
    
    /**
     * Edit question modal actions
     */
    this.addNewQuestion = function() {
      /**
       * Adds a new question based on information from this.currentQuestionFields
       */
      var questionObject = this.getCurrentQuestionObject();
      // Generate a new UUID since this is a new question
      questionObject["question_id"] = uuid.generate();
      this.questions.push(questionObject);
    };

    this.editQuestion = function() {
      /**
       * Edits the question in this.questions based on information in this.currentQuestionFields\
       */
      var questionObject = this.getCurrentQuestionObject();
      this.questions.splice(this.currentQuestionFields.index, 1, questionObject);
    };
    
    this.addAnswerField = function() {
      /**
       * Adds a field to this.currentQuestionFields.answers array
       */
      this.currentQuestionFields.answers.push({"text": ""});
    };
    
    this.deleteAnswerField = function(index) {
      /**
       * Removes the field in this.currentQuestionFields.answers array at the passed index
       */
      this.currentQuestionFields.answers.splice(index, 1);
    };

    
    /**
     * Edit question modal helper functions
     */
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
      /**
       * Populates the edit question modal with information from the question in this.questions at the passed index 
       */
      this.resetQuestionModal(this.questions[index]);
      this.currentQuestionFields.is_new_question = false;
      this.currentQuestionFields.index = index;
    };
    
    this.getCurrentQuestionObject = function() {
      /**
       * Returns an object with the correct fields for sending to the backend from data in this.currentQuestionFields
       */
      var questionType = this.currentQuestionFields.question_type;
      return _.pick(this.currentQuestionFields, QUESTION_FIELDS_LIST[questionType]);
    };
    
    this.checkSliderValue = function(min_or_max) {
      /**
       * Checks if a slider value (min or max) is within the allowed range. If not, sets it to the minimum
       * or maximum depending on which side it is out of range on.
       */
      var input = $("#" + min_or_max);
      var minimumValue = input.attr("min");
      var maximumValue = input.attr("max");
      if (input.val() < minimumValue) {
        this.currentQuestionFields[min_or_max] = minimumValue;
      } else if (input.val() > maximumValue) {
        this.currentQuestionFields[min_or_max] = maximumValue;
      }
    };

    /**
     * Question summary actions
     */
    this.moveQuestionUp = function(index) {
      /**
       * Move the question at the passed index up in order in this.questions
       */
      if (index > 0) {
        this.questions.splice(index-1, 2, this.questions[index], this.questions[index-1]);
      }
    };
    
    this.moveQuestionDown = function(index) {
      /**
       * Move the question at the passed index down in order in this.questions
       */
      if (index < this.questions.length-1) {
        this.questions.splice(index, 2, this.questions[index+1], this.questions[index]);
      }
    };
    
    this.deleteQuestion = function(index) {
      /**
       * Delete the question at the passed index in this.questions
       */
      this.questions.splice(index, 1);
    };
    
  }

})();