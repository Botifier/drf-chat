import json

from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError

from rest_framework.test import APITestCase, APITransactionTestCase
from rest_framework.views import status

from django.contrib.auth.models import User
from .models import Conversation, Message
from .serializers import MessageSerializer, ConversationSerializer, MessageListSerializer


class BaseViewTest(APITestCase):

    username1 = 'mouath'
    email1 = 'mouath@mouath.mouath'
    username2 = 'mouath1'
    email2 = 'mouath1@mouath.mouath'
    password = 'pass1234'
    
    def setUp(self):
        self._create_test_users()
        self._create_test_conversation()
        self.conversation = Conversation.objects.get()
        self._create_test_message()  
        self._get_jwt_token()      

    def _create_test_message(self):
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            text='okbb' 
            )

    def _create_test_conversation(self):
        obj = Conversation()
        obj.save()
        obj.participants.add(self.user1)
        obj.participants.add(self.user2)

    def _create_test_users(self):
        self.user1 = User.objects.create_user(self.username1, self.email1, self.password)
        self.user2 = User.objects.create_user(self.username2, self.email2, self.password)

    def _get_jwt_token(self):
        url = reverse('api-token-auth')
        response = self.client.post(
            url, 
            {'username':self.username1, 'password':self.password},
             format='json'
            )        
        self.jwt_token = response.data['token']

    def jwt_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.jwt_token)

    @classmethod
    def jwt_auth_before(cls, func):
        def wrapper(self):
            self.jwt_auth()
            func(self)
        return wrapper


class ConversationListViewTest(BaseViewTest):

    def setUp(self):
        super(ConversationListViewTest, self).setUp()
        self.url = reverse('conversation-list')        

    def test_get_conversationlist_authorisation(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    
    def test_post_conversationlist_authorisation(self):
        response = self.client.post(self.url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    @BaseViewTest.jwt_auth_before    
    def test_get_conversationlist(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected = Conversation.objects.all()
        serialized = ConversationSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
    
    @BaseViewTest.jwt_auth_before
    def test_post_conversationlist(self):
        response = self.client.post(self.url, {'with':'mouath1'})
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        expected = Conversation.objects.all()
        serialized = ConversationSerializer(expected, many=True)
        data = serialized.data   
        self.assertEqual(len(data), 2)
        self.assertEqual(data[1]['participants'], ['mouath', 'mouath1'])


class MessageListViewTest(BaseViewTest):

    def setUp(self):
        super(MessageListViewTest, self).setUp()
        self.url = reverse('message-list')    
                            
    def test_get_messagelist_authorisation(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    
    def test_post_messagelist_authorisation(self):
        response = self.client.post(self.url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    @BaseViewTest.jwt_auth_before    
    def test_get_messagelist(self):
        response = self.client.get(self.url, {'conversation':self.conversation.uid})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected = Message.objects.all()
        serialized = MessageListSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)

    @BaseViewTest.jwt_auth_before
    def test_post_messagelist(self):
        #TODO: add test non existing message
        response = self.client.post(
            self.url,
             {'conversation':self.conversation.uid,
              'text': 'blablabla',
              })
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        expected = Message.objects.all()
        serialized = MessageSerializer(expected, many=True)
        data = serialized.data   
        self.assertEqual(len(data), 2)
        self.assertEqual(data[1]['text'], 'blablabla')
        #test empty message
        response = self.client.post(
            self.url,
             {'conversation':self.conversation.uid,
              'text': '',
              })
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)


class MessageDetailViewTest(BaseViewTest):

    def setUp(self):
        super(MessageDetailViewTest, self).setUp()
        self.url = reverse('message-detail')

    def test_get_messagedetail_authorisation(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    
    @BaseViewTest.jwt_auth_before
    def test_get_messagedetail(self):
        response = self.client.get(self.url, {'msg_id':self.message.uid})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected = Message.objects.get(uid=self.message.uid)
        serialized = MessageSerializer(expected)
        self.assertEqual(response.data, serialized.data)


class JWTAuthTest(APITestCase):

    def setUp(self):
        self.username = 'mouath'
        self.email = 'mouath@mouath.mouath'
        self.password = 'pass1234'
        self.create_url = reverse('api-token-auth')
        self.verify_url = reverse('api-token-verify')
        self._create_user()
    
    def _req_token(self):
        response = self.client.post(
            self.create_url, 
            {'username':self.username, 'password':self.password},
            format='json'
        )        
        return response
    
    def _verif_token(self, token):
        response = self.client.post(
            self.verify_url,
            {'token': token}, 
            format='json'
        )
        return response

    def _create_user(self):
        User.objects.create_user(
            'mouath', 
            'mouath@mouath.mouath',
            'pass1234'
        )

    def test_token_valid(self):
        response = self._req_token()
        data = response.data
        self.assertTrue('token' in data)
        token = data['token']
        self.assertEqual(
            self._verif_token('UNVALID_TOKEN').status_code, 
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self._verif_token(token).status_code,
            status.HTTP_200_OK
        )
        

class RegisterTest(APITransactionTestCase):
    
    def setUp(self):
        self.register_url = reverse('register')
        self.verify_url = reverse('api-token-verify')
        self.username = 'yoyo'
    
    def _verif_token(self, token):
        response = self.client.post(
            self.verify_url,
            {'token': token}, 
            format='json'
        )
        return response

    def test_post_registration(self):
        response = self.client.post(self.register_url, {'username': self.username})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        token = response.data
        self.assertEqual(
            self._verif_token(token).status_code,
            status.HTTP_200_OK
        )

    def test_get_or_create(self):
        self.client.post(self.register_url, {'username': self.username})               
        response = self.client.post(self.register_url, {'username': self.username})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)




