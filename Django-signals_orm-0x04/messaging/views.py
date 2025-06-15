from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
    """View for a conversation between two users"""
    other_user = get_object_or_404(User, pk=user_id)
    messages = Message.objects.get_conversation(request.user, other_user)

    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'messages': messages
    })


@login_required
def thread_view(request, message_id):
    """View for a specific message thread"""
    message = get_object_or_404(Message.objects.select_related('sender', 'receiver'), pk=message_id)
    thread = message.get_thread()

    return render(request, 'messaging/thread.html', {
        'root_message': message,
        'thread': thread
    })
