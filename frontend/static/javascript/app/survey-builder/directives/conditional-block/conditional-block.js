angular.module("surveyBuilder")
  .directive("conditionalBlock", function(_, ARITHMETIC_OPERATORS) {
    return {
      "link": function(scope) {
        scope._ = _;
        scope.type = _.keys(scope.surveyBuilder.getValueAtPath(scope.path))[0];
        scope.ARITHMETIC_OPERATORS = ARITHMETIC_OPERATORS;
        
        scope.getQuestionNumber = function(index) {
          return "Q" + ++index;
        }
      },
      "restrict": "E",
      "scope": {
        "surveyBuilder": "=",
        "path": "@"
      },
      "templateUrl": "/static/javascript/app/survey-builder/directives/conditional-block/conditional-block.html"
    };
  });
