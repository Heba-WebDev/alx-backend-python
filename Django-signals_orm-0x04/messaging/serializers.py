from rest_framework.serializers import ModelSerializer
from .models import Message

class MessageSerializer(ModelSerializer):
    """Serializer for the Message model."""
    class Meta:
        """Meta class for MessageSerializer."""

        model = Message
        fields = "__all__"