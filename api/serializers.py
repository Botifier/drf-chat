from rest_framework import serializers

from .models import User, Message, Conversation

#TODO: add tests on the returned fields
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('uid', 'sender', 'created_at', 'text', 'conversation')
        # read_only_fields = ('created_at')
        extra_kwargs = {'conversation': {'write_only': True}}


class MessageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('uid', 'conversation')
        # read_only_fields = ('created_at')
        extra_kwargs = {'conversation': {'write_only': True}}


class ConversationSerializer(serializers.ModelSerializer):    
    participants = serializers.SlugRelatedField(many=True, slug_field='username', queryset=User.objects.all())
    
    class Meta:
        model = Conversation
        fields = ('uid', 'updated_at', 'participants')
        read_only_fields = ('uid', 'updated_at')
    #TODO: add highlight methodfield (getting message[:12])


# class RegistrationSerializer(serializers.ModelSerializer):
#     def create(self, validated_data):
#         return User.objects.create(**validated_data)

#     class Meta:
#         model = User
#         fields = ('username', 'password', 'email')






