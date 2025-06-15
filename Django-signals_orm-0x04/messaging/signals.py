from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Message, Notification, MessageHistory, User

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """Creates a notification for the receiver when a new message is created."""
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            is_read=False
        )

@receiver(pre_save, sender=Message)
def log_message_history(sender, instance, **kwargs):
    """ Logs the old content of a message before it's updated """
    if instance.pk:
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender
                )
                instance.edited = True
                instance.last_edited = timezone.now()
        except Message.DoesNotExist:
            pass


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up related data when a user is deleted.
    This handles cases where CASCADE isn't appropriate or we need additional cleanup.
    """
    # Messages where user is sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Notifications for the user
    Notification.objects.filter(user=instance).delete()

    # Message histories edited by the user
    MessageHistory.objects.filter(edited_by=instance).update(edited_by=None)
