from django.db import models

class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        """
        Returns unread messages for a specific user with optimized queries
        using select_related and only to fetch minimal required fields
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).select_related('sender').only(
            'id',
            'content',
            'timestamp',
            'sender__id',
            'sender__username',
            'is_read'  # Needed for the filter
        ).order_by('-timestamp')
