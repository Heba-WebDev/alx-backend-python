from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

User = get_user_model()

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')  # Replace with your home URL name
    return render(request, 'messaging/confirm_delete.html')
