from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)  # Related_name='messages'

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']