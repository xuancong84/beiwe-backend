(function() {
  
  angular
    .module("surveyBuilder")
    .controller("SurveyBuilderCtrl", SurveyBuilderCtrl);
  
  function SurveyBuilderCtrl(_, QUESTION_FIELDS_LIST, QUESTION_TYPE_LABELS, QUESTION_TYPES,
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
      "answers": [],
      "display_if": null/*{'or': [
                         {'and': [
                                  {'==': ['6695d6c4-916b-4225-8688-89b6089a24d1', 4]},
                                  {'or': [
                                           {'>=': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 2]},
                                           {'>=': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 2]}
                                          ]}
                                 ]},
                         {'or': [
                                 {'>=': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 3]},
                                 {'>=': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 3]}
                                ]}
                        ]}*/
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
       *
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
      var currentValue = parseInt(input.val(), 10);
      var minimumValue = parseInt(input.attr("min"), 10);
      var maximumValue = parseInt(input.attr("max"), 10);
      if (currentValue < minimumValue) {
        this.currentQuestionFields[min_or_max] = minimumValue;
      } else if (currentValue > maximumValue) {
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
        this.questions.splice(index - 1, 2, this.questions[index], this.questions[index - 1]);
      }
    };

    this.moveQuestionDown = function(index) {
      /**
       * Move the question at the passed index down in order in this.questions
       */
      if (index < this.questions.length - 1) {
        this.questions.splice(index, 2, this.questions[index + 1], this.questions[index]);
      }
    };

    this.deleteQuestion = function(index) {
      /**
       * Delete the question at the passed index in this.questions
       */
      this.questions.splice(index, 1);
    };

    /**
     * Skip logic actions
     */
    this.addOrBlock = function(path) {
      /**
       * Adds an OR block to the display_if nested object at the path specified (path should be a string that's
       * "/" delimited to where the OR block should be added).
       */
      this.addValueToPath(path, {"or": []})
    };

    this.addConditional = function(path) {
      this.addValueToPath(path, "asdf")
    };

    /**
     * Skip logic helper functions
     */
    this.getPathLocation = function(path) {
      /**
       * Navigates to the passed in path from this.currentQuestionFields.display_if and returns and array with
       * the parent location and last key. For example, if the path is "or/3", the referenced location is
       * this.currentQuestionFields.display_if["or"]["3"], and this function will return
       * [this.currentQuestionFields.display_if["or"], "3"].
       *
       * Args:
       *   path (string): the path to navigate to
       * Returns:
       *   (array): [parentLocation (object/array), lastKey (string)]
       */
      var pathKeys = ["display_if"].concat(path.match(/[^\/]+/g) || []);
      var lastKey = pathKeys.pop();
      var currentLocation = this.currentQuestionFields;
      _.forEach(pathKeys, function(key) {
        if (typeof currentLocation === "undefined") {
          alert("Sorry, something went wrong with adding this field (" + path + ").");
          return false;
        }
        currentLocation = currentLocation[key]
      });
      return [currentLocation, lastKey]
    };
    
    this.getValueAtPath = function(path) {
      var pathLocationArray = this.getPathLocation(path);
      var parentObject = pathLocationArray[0];
      var key = pathLocationArray[1];
      return parentObject[key];
    };
    
    this.addValueToPath = function(path, value) {
      /**
       * Adds the passed value to the path from root this.currentQuestionFields.display_if
       */
      var pathLocationArray = this.getPathLocation(path);
      var parentObject = pathLocationArray[0];
      var key = pathLocationArray[1];
      if (parentObject[key] == null) {
        parentObject[key] = value;
      } else if (_.isArray(parentObject[key])) {
        parentObject[key].push(value);
      }
    }
    
  }

})();