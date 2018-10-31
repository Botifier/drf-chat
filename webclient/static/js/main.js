var app = angular.module('chatapp', [
  'ui.router',
  'satellizer'
]);

app.constant('URLS', {
  'base': 'http://localhost:8000/api/',
  'register': 'register/',
})

app.config(function($stateProvider, $urlRouterProvider, $authProvider){
	$stateProvider
		.state('register', {
			url: '/',
			templateUrl: '/static/templates/register.html',
      controller: 'RegisterCtrl',
      data: {loggedIn: false}
		})
		.state('chat', {
			url: '/chat',
			templateUrl: '/static/templates/chat.html',
      controller: 'ChatCtrl',
      data: {loggedIn: true}
		});

  $urlRouterProvider.otherwise('/');
  $authProvider.tokenType = 'JWT'
});


app.controller('RegisterCtrl', function($scope, AuthService, $state, $auth){
  $scope.username = ''
  $scope.register = function(){
    AuthService.register($scope.username).then(
      function(res){        
        if (res.status == 201){
          console.log($auth)
          $auth.setToken(res.data);
          $state.go('chat')
        }
      }
    )
  }  
})

app.controller('ChatCtrl', function($scope, ChatService){

})

app.service('AuthService', function($http, URLS){
  var Auth = {};
  REGISTER_URL = URLS.base + URLS.register  
  Auth.register = function(username){
    return $http.post(REGISTER_URL, {'username': username})
  }
  return Auth;
})

app.service('ChatService', function($http, URLS){
});

app.run(function ($rootScope, $state, $auth) {
  $rootScope.$on('$stateChangeStart',
    function (event, toState) {
      var loggedIn = false;
      if (toState.data && toState.data.loggedIn){
        loggedIn = toState.data.loggedIn;      
      }
      if (loggedIn && !$auth.isAuthenticated()) {
        event.preventDefault();
        $state.go('register');
      }
      else if (!loggedIn && $auth.isAuthenticated()) {
        event.preventDefault();
        $state.go('chat');
      }
    });
});