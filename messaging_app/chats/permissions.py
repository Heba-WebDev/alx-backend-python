from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        elif isinstance(obj, Message):
            if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
            return False
        return False
