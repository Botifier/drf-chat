from rest_framework import serializers

from .models import User, Message, Conversation


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('uid', 'sender', 'created_at', 'text', 'conversation')
        # read_only_fields = ('created_at')


class ConversationSerializer(serializers.ModelSerializer):    
    participants = serializers.SlugRelatedField(many=True, slug_field='username', queryset=User.objects.all())
    
    class Meta:
        model = Conversation
        fields = ('uid', 'updated_at', 'participants')
        read_only_fields = ('uid', 'updated_at')
    #TODO: add highlight methodfield (getting message[:12])





