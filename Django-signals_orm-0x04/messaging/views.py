from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_200_OK
from .serializers import MessageSerializer
from .models import Message
from django.shortcuts import render, get_object_or_404

User = get_user_model()

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')  # Replace with your home URL name
    return render(request, 'messaging/confirm_delete.html')


@login_required
def conversation_view(request, user_id):
    """View for a conversation between two users with optimized queries"""
    other_user = get_object_or_404(User, pk=user_id)

    # Optimized query using select_related and prefetch_related
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).select_related('sender', 'receiver').prefetch_related(
        'replies__sender', 'replies__receiver'
    ).order_by('timestamp')

    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'messages': [m for m in messages if not m.parent_message]
    })


@login_required
def thread_view(request, message_id):
    """View for a specific message thread with recursive replies"""
    root_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        pk=message_id
    )

    # Recursive query to get all replies
    def get_replies(message, depth=0):
        replies = list(message.replies.all()
                       .select_related('sender', 'receiver')
                       .order_by('timestamp'))
        result = []
        for reply in replies:
            result.append((reply, depth))
            result.extend(get_replies(reply, depth + 1))
        return result

    thread = get_replies(root_message)

    return render(request, 'messaging/thread.html', {
        'root_message': root_message,
        'thread': thread
    })


@login_required
def reply_view(request, message_id):
    """Handle message replies"""
    if request.method == 'POST':
        parent_message = get_object_or_404(Message, pk=message_id)
        Message.objects.create(
            sender=request.user,
            receiver=parent_message.sender if request.user == parent_message.receiver else parent_message.receiver,
            content=request.POST.get('content'),
            parent_message=parent_message
        )
        return redirect('messaging:thread', message_id=message_id)
    return redirect('messaging:conversation', user_id=request.user.id)


@login_required
def inbox_unread(request):
    """View showing only unread messages using the custom manager"""
    # Using the custom manager with optimized query
    unread_messages = Message.unread.for_user(request.user)
    Message.unread.unread_for_user = True
    # Message.objects.only(
    #     'sender',
    #     'receiver', )
    return render(request, 'messaging/inbox_unread.html', {
        'unread_messages': unread_messages
    })


@login_required
def mark_message_read(request, message_id):
    """Mark a specific message as read"""
    message = get_object_or_404(
        Message.unread.for_user(request.user),  # Using our custom manager
        pk=message_id
    )
    message.mark_as_read()
    return redirect('messaging:inbox_unread')


@login_required
def conversation_unread(request, user_id):
    """Show unread messages in a specific conversation"""
    # Using the custom manager with additional filtering
    unread_messages = Message.unread.for_user(request.user).filter(
        sender_id=user_id
    )

    return render(request, 'messaging/conversation_unread.html', {
        'unread_messages': unread_messages,
        'sender_id': user_id
    })

@cache_page(60)  # Cache the response for 60 seconds
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_user_messages(request: Request) -> Response:
    """
    View to get all messages for the authenticated user.
    """

    if not request:
        return Response(
            {"error": "Request object is missing."},
            status=HTTP_400_BAD_REQUEST,
        )

    user: User = request.user

    if not user.is_authenticated:
        return Response(
            {"error": "User is not authenticated."},
            status=HTTP_401_UNAUTHORIZED,
        )

    # Fetch all messages for the user (both sent and received)
    replies = (
        Message.objects.filter(user=user)
        .select_related("sender", "recipient")
        .prefetch_related("parent_message")
        .filter(Q(sender=request.user) | Q(recipient=user))
    )

    if not replies.exists():
        return Response(
            {"message": "No messages found for the user."},
            status=HTTP_404_NOT_FOUND,
        )

    serializer = MessageSerializer(replies, many=True)
    return Response(serializer.data, status=HTTP_200_OK)