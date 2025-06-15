from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()


class SignalTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass123')
        self.receiver = User.objects.create_user(username='receiver', password='testpass123')

    def test_notification_created_on_message_save(self):
        """Test that a notification is created when a new message is saved"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )

        # Check that a notification was created
        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)
