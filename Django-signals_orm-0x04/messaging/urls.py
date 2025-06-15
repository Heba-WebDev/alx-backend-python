from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_user'),
    path('conversation/<int:user_id>/', views.conversation_view, name='conversation'),
    path('thread/<int:message_id>/', views.thread_view, name='thread'),
    path('reply/<int:message_id>/', views.reply_view, name='reply'),
    path('unread/', views.unread_messages, name='unread'),
    path('mark-read/<int:message_id>/', views.mark_as_read, name='mark_read'),
]
