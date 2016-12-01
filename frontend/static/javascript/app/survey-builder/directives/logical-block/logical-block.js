angular.module("surveyBuilder")
  .directive("logicalBlock", function(_, ARITHMETIC_OPERATORS, LOGICAL_OPERATORS) {
    return {
      "restrict": "E",
      "scope": {
        "surveyBuilder": "=",
        "path": "@"
      },
      "link": function(scope) {
        scope._ = _;
        scope.ARITHMETIC_OPERATORS = ARITHMETIC_OPERATORS;
        scope.LOGICAL_OPERATORS = LOGICAL_OPERATORS;
      },
      "templateUrl": "/static/javascript/app/survey-builder/directives/logical-block/logical-block.html"
    };
  });
