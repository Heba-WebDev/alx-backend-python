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
    sender_email = serializers.CharField(source='sender.email', read_only=True) 

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_email', 'conversation', 'content', 'timestamp']

    def validate_content(self, value):  # ← ValidationError example
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)  # Related_name='messages'

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']