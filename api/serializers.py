from rest_framework import serializers

from .models import User, Message, Conversation

#TODO: add tests on the returned fields
class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('uid', 'sender', 'created_at', 'text', 'conversation', 'sender_name')
        # read_only_fields = ('created_at')
        extra_kwargs = {'conversation': {'write_only': True}}

    def get_sender_name(self, obj):
        user = User.objects.get(id=obj.sender.id)
        return user.username


class ConversationSerializer(serializers.ModelSerializer):    
    participants = serializers.SlugRelatedField(many=True, slug_field='username', queryset=User.objects.all())
    
    class Meta:
        model = Conversation
        fields = ('uid', 'updated_at', 'participants')
        read_only_fields = ('uid', 'updated_at')
    #TODO: add highlight methodfield (getting message[:12])







