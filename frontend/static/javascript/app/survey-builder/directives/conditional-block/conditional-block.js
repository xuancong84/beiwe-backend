angular.module("surveyBuilder")
  .directive("conditionalBlock", function(_) {
    return {
      "link": function(scope) {
        scope._ = _;
      },
      "restrict": "E",
      "scope": {
        "surveyBuilder": "=",
        "path": "@"
      },
      "templateUrl": "/static/javascript/app/survey-builder/directives/conditional-block/conditional-block.html"
    };
  });
