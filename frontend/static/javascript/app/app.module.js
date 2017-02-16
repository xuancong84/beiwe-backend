angular.module("surveyBuilder", ['ngRaven'])
  .factory("_", function($window) {
    /**
     * Load lodash for use in angular
     */
    if (!$window._) {
      location.reload();
    }
    return $window._;
  });
