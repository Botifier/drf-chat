from .models import Conversation, User, Message
from .serializers import MessageSerializer, ConversationSerializer
from django.http import Http404
from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

#TODO: seperate the views in different files under views/

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
        messages = Message.objects.filter(conversation=Conversation.objects.get(uid=request.GET.get('conversation')))
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    ''' Create new message '''
    def post(self, request):        
        data = {
            'sender': request.user.id,
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
    #TODO: make this function reusable by other classes
    def get_object(self, uid):
        try:
            return Message.objects.get(uid=uid)
        except Message.DoesNotExist:
            raise Http404

    def get(self, request):
        message = self.get_object(request.GET.get('msg_id'))
        serializer = MessageSerializer(message)
        return Response(serializer.data)













