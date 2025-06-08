from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model
from .permissions import IsParticipantOfConversation

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        return self.queryset.filter(participants=self.request.user)
    
    def create(self, request, *args, **kwargs):
        user_ids = request.data.get('participants', [])
        if not user_ids:
            return Response({"detail": "At least one participant is required."},
                            status=status.HTTP_400_BAD_REQUEST)
        participant_ids = list(set(user_ids + [request.user.user_id]))
        try:
            participants = User.objects.filter(user_id__in=participant_ids)
        except User.DoesNotExist:
            return Response({"detail": "Invalid user IDs provided."},
                          status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.create()
        conversation.participants.set(User.objects.filter(id__in=participant_ids))
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        """Return messages from conversations the user is part of."""
        queryset = Message.objects.filter(conversation__participants=self.request.user)
        conversation_id = self.kwargs.get('conversation_conversation_id') or self.request.query_params.get('conversation')
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['sender'] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not Message.objects.filter(
            id=instance.id,
            conversation__participants=self.request.user
        ).exists():
            return Response(
                {"detail": "You are not authorized to update this message"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
