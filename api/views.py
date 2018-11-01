from .models import Conversation, User, Message
from .serializers import (
    MessageSerializer, 
    ConversationSerializer, 
    MessageListSerializer
)
from django.http import Http404
from django.shortcuts import render
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings


class ConversationList(APIView):
    
    ''' get conversations list '''
    def get(self, request):
        conversations = Conversation.objects.filter(participants__id=request.user.id) 
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)
    
    ''' Create new conversation 
        POST {"with": "user2id"}  
    '''
    def post(self, request):        
        #edit to just send usernames
        participants = [request.user, User.objects.get(username=request.data['with'])]
        data = {'participants': participants}
        serializer = ConversationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageList(APIView):

    ''' Return message list'''
    def get(self, request):
        try:
            conversation = Conversation.objects.get(uid=request.GET.get('conversation'))
        except Conversation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        messages = Message.objects.filter(conversation=conversation)
        serializer = MessageListSerializer(messages, many=True)
        return Response(serializer.data)

    ''' Create new message '''
    def post(self, request):        
        data = {
            'sender': request.user.id,# TODO: change to name then resolve name to id
            'conversation': Conversation.objects.get(uid=request.data['conversation']).id,
            'text': request.data['text']
        }
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageDetail(APIView):

    ''' Get message details from id '''
    def get_object(self, uid):
        try:
            return Message.objects.get(uid=uid)
        except Message.DoesNotExist:
            raise Http404

    def get(self, request):
        message = self.get_object(request.GET.get('msg_id'))
        serializer = MessageSerializer(message)
        return Response(serializer.data)


class Registration(APIView):
    permission_classes = ()
    #TODO: add when user is already registered case
    
    def create_user(self, username):                
        password = get_random_string()
        email = get_random_string() + '@co.co'  
        try:               
            user = User.objects.create_user(username, email, password)
        except: #user already exists
            user = User.objects.get(username=username)
        return user
    
    def get_token(self, user):
        payload = api_settings.JWT_PAYLOAD_HANDLER(user)
        token = api_settings.JWT_ENCODE_HANDLER(payload)
        return token

    def post(self, request):
        token = self.get_token(self.create_user(request.data['username']))
        return Response(token, status=status.HTTP_201_CREATED)


















