angular.module("surveyBuilder", [])
  .factory("_", function($window) {
    /**
     * Load lodash for use in angular
     */
    if (!$window._) {
      window.reload();
    }
    return $window._;
  });
