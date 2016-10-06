/* Because there already is one ng-app on the page (the filter/search field in
the navigation bar View Study selector), all other ng-apps must be bootstrapped
separately. */

var FilterableListApp = angular.module("FilterableListApp", []);

FilterableListApp.controller('FilterableListController', function($scope){})

$(document).ready(function(){
	angular.bootstrap(document.getElementById('filterableList'), ['FilterableListApp'])
});
