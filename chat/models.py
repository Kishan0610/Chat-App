from django.contrib.auth.models import User
from django.db import models

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}"


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups")
    members = models.ManyToManyField(User, related_name="chat_groups")  # Changed related_name to "chat_groups"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name 

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
