from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q, Prefetch

User = get_user_model()

class MessageManager(models.Manager):
    def get_conversation(self, user1, user2):
        return self.filter(
            Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1)
        ).select_related('sender', 'receiver').prefetch_related(
            Prefetch('replies',
                    queryset=Message.objects.select_related('sender', 'receiver')
                    .order_by('timestamp'))
        ).order_by('timestamp')

    def get_thread(self, message_id):
        """Get a message and all its replies recursively"""
        return self.filter(
            Q(id=message_id) | Q(parent_message_id=message_id)
        ).select_related('sender', 'receiver', 'parent_message').order_by('timestamp')


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    last_edited = models.DateTimeField(null=True, blank=True)

    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    objects = MessageManager()

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

    def get_thread(self):
        """Recursive method to get all replies in a thread"""
        replies = list(self.replies.all().select_related('sender', 'receiver'))
        for reply in replies:
            replies.extend(reply.get_thread())
        return replies


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Message Histories'

    def __str__(self):
        return f"History for message {self.message.id} at {self.changed_at}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"
