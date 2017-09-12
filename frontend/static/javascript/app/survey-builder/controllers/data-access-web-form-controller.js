(function(){
    angular
    .module('surveyBuilder')
    .controller('DataAccessWebFormController', ['$scope', '$window', function($scope, $window) {
        $scope.allowedStudies = $window.allowedStudies;
        $scope.participantsByStudy = $window.participantsByStudy
        $scope.selectedStudy = $scope.allowedStudies[0];
    }]);
}());
