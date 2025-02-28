from django.contrib import admin
from django.utils import timezone
from .models import Message, Group, GroupMessage

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp')

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at')
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'content', 'timestamp')
    list_filter = ('group',)  # Adds a filter sidebar to filter messages by group
    search_fields = ('content', 'sender__username', 'group__name')  # Allows searching by content, sender, or group name

admin.site.register(Message, MessageAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMessage, GroupMessageAdmin)

admin.site.site_header = "Chat-App Administration"  # Change header text
admin.site.site_title = "Chat-App Admin Portal"  # Change browser tab title
admin.site.index_title = "Welcome to Chat-App Admin Panel"
