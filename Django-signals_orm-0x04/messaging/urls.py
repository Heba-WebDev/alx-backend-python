from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_user'),
    path('conversation/<int:user_id>/', views.conversation_view, name='conversation'),
    path('thread/<int:message_id>/', views.thread_view, name='thread'),
]
