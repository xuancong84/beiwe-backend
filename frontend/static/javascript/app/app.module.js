angular.module("surveyBuilder", [])
  .run(function($rootScope) {
    /**
     * Load lodash for use in angular templating
     */
    $rootScope._ = window._;
  });