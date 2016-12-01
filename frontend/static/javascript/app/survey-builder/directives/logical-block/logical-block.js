angular.module("surveyBuilder")
  .directive("logicalBlock", function(_, ARITHMETIC_OPERATORS, LOGICAL_OPERATORS) {
    return {
      "link": function(scope) {
        /* Constants */
        scope._ = _;
        scope.ARITHMETIC_OPERATORS = ARITHMETIC_OPERATORS;
        scope.LOGICAL_OPERATORS = LOGICAL_OPERATORS;
        
        scope.type = _.keys(scope.surveyBuilder.getValueAtPath(scope.path))[0];
        scope.getNewPath = function(index) {
          var newPath = scope.path + "/" + scope.type;
          if (typeof index != "undefined") {
            newPath = newPath + "/" + index;
          }
          return newPath;
        }
      },
      "restrict": "E",
      "scope": {
        "surveyBuilder": "=",
        "path": "@"
      },
      "templateUrl": "/static/javascript/app/survey-builder/directives/logical-block/logical-block.html"
    };
  });
