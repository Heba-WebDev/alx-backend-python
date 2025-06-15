from django.contrib import admin
from .models import Message, Notification, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    extra = 0
    readonly_fields = ('changed_at', 'edited_by')
    can_delete = False

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_read', 'edited', 'last_edited')
    list_filter = ('is_read', 'timestamp', 'edited')
    search_fields = ('sender__username', 'receiver__username', 'content')
    inlines = [MessageHistoryInline]

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username',)

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'changed_at', 'edited_by')
    list_filter = ('changed_at',)
    search_fields = ('message__content', 'old_content')
    readonly_fields = ('message', 'old_content', 'changed_at', 'edited_by')
