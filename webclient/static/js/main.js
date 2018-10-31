var app = angular.module('chatapp', [
  'ui.router',
  'satellizer'
]);

app.constant('URLS', {
  'base': 'http://localhost:8000/api/',
  'register': 'register/',
  'conversation_list': 'conversations/',
  'message_list': 'messages/',
  'message_detail': 'message/',
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
  let Chat = {};
  const CLIST_URL = URLS.base + URLS.conversation_list
  const MLIST_URL = URLS.base + URLS.message_list
  const MDETAIL_URL = URLS.base + URLS.message_detail
	Chat.getConversations = function(){
		return $http.get(CLIST_URL);
	};
  Chat.getMessages = function(){
		return $http.get(MLIST_URL);
  };
  Chat.getMessage = function(uid){
		return $http.get(MDETAIL_URL, uid);
  };  
  Chat.addConversation = function(with_){
    return $http.post(CLIST_URL, with_)
  }
  Chat.addMessage = function(details){ //details:{conversationId, messageText}
    return $http.post(MLIST_URL, details)
  }
	return Chat;
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