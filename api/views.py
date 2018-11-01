import json
from .models import Conversation, User, Message
from .serializers import (
    MessageSerializer, 
    ConversationSerializer, 
)
from django.http import Http404
from django.shortcuts import render
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from channels import Group
from django.contrib.auth import login

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
        user = User.objects.get(username=request.data['with'])
        participants = [request.user, user]
        data = {'participants': participants}
        serializer = ConversationSerializer(data=data)
        if serializer.is_valid():
            conversation = serializer.save()
            receiver_id = user.id
            Group(str(receiver_id)).send({
                'text': json.dumps({
                    'event': 'NEWCONVERSATION',
                    'conversation': str(conversation.uid),
                    'with': str(request.user.username)
                })
            })
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
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    ''' Create new message '''
    def post(self, request): 
        conversation = Conversation.objects.get(uid=request.data['conversation'])       
        data = {
            'sender': request.user.id,# TODO: change to name then resolve name to id
            'conversation': conversation.id,
            'text': request.data['text']
        }
        for user in conversation.participants.all():
            if user.id != request.user.id:
                receiver_id = user.id
                break
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            message = serializer.save()
            Group(str(receiver_id)).send({
                'text': json.dumps({
                    'event': 'NEWMESSAGE',
                    'conversation': str(conversation.uid),
                    'message': str(message.uid),
                    'sender_name': str(request.user.username)
                })
            })
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
    
    def create_user(self, username, request):                
        password = get_random_string()
        email = get_random_string() + '@co.co'  
        try:               
            user = User.objects.create_user(username, email, password)
        except: #user already exists
            user = User.objects.get(username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return user
    
    def get_token(self, user):
        payload = api_settings.JWT_PAYLOAD_HANDLER(user)
        token = api_settings.JWT_ENCODE_HANDLER(payload)
        return token

    def post(self, request):
        token = self.get_token(self.create_user(request.data['username'], request))
        return Response(token, status=status.HTTP_201_CREATED)


















