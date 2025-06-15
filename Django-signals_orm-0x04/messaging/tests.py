from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory
from django.utils import timezone

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

        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)

    def test_message_history_on_edit(self):
        """Test that message history is logged when a message is edited"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )

        # Edit the message
        message.content = "Edited content"
        message.save()

        # Check history was created
        self.assertEqual(MessageHistory.objects.count(), 1)
        history = MessageHistory.objects.first()
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.message, message)
        self.assertEqual(history.edited_by, self.sender)

        # Check message was marked as edited
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertIsNotNone(message.last_edited)

    def test_no_history_on_initial_create(self):
        """Test that no history is created for new messages"""
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        self.assertEqual(MessageHistory.objects.count(), 0)
