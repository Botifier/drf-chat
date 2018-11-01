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


app.controller('RegisterCtrl', function($scope, AuthService, $state, $auth, UserData){
  $scope.username = ''
  $scope.register = function(){
    AuthService.register($scope.username).then(
      function(res){        
        if (res.status == 201){
          $auth.setToken(res.data);  
          UserData.setname($scope.username)
          $state.go('chat')
        }
      }
    )
  }  
})

// conversation = uid, participants, updated_at
app.controller('ChatCtrl', function($scope, ChatService, UserData){
  // ChatService.addConversation({'with': 'lam3i'}).then(    ()=>
  $scope.username = UserData.getname()
  $scope.conversations = {}
  ChatService.getConversations().then(
    function(res){
      if (res.status == 200){
        let conversations = res.data
        for (i in conversations){
          participants = conversations[i].participants
          var index = participants.indexOf($scope.username);
          var other;
          if (index > -1) {
            participants.splice(index, 1);
            other = participants[0]
          }
          conversations[i].other = other
        }
        $scope.conversations = conversations

      }
    }
  )

  //takes uid of conversation to highlight
  $scope.selectConversation = function(conversationUid){
    $scope.messageList = []
    $scope.selectedConversation = conversationUid
    ChatService.getMessages(conversationUid).then(
      function(res){
        if (res.status == 200){
          let messages = res.data
          for (var i in messages){
            if (i >= 10){
              break
            }
            //fetch maximum 10 last messages
            ChatService.getMessage(messages[i].uid).then(
              function(res){
                $scope.messageList.push(res.data)
              }
            )
            
          }
        }
      }
    )
  }



  

  $scope.sendMessage = function(msgText){
    ChatService.addMessage({
      'conversation': $scope.selectedConversation,
      'text': msgText
    }).then(function(res){
      if (res.status == 201){
        $scope.messageList.push({'text':msgText, 'created_at':Date.now()})
        $scope.message = ""
      }
    })
  }

  




  // )

})

app.service('UserData', function(){
  var UserData = {}
  UserData.setname = function(username){
    window.localStorage['username'] = JSON.stringify(username);
  }
  UserData.getname = function(){
    return angular.fromJson(window.localStorage['username']);
  }
  return UserData
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
  Chat.getMessages = function(conversationUId){
		return $http.get(MLIST_URL, {params: {conversation: conversationUId}});
  };
  Chat.getMessage = function(msgUid){
		return $http.get(MDETAIL_URL, {params: {msg_id: msgUid}});
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