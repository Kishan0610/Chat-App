import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from django.contrib.auth.models import User

# Initialize logger
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender = self.scope['user']
        self.recipient_username = self.scope['url_route']['kwargs'].get('recipient')
        self.room_name = (
            f"chat_{min(self.sender.username, self.recipient_username)}_{max(self.sender.username, self.recipient_username)}"
        )
        logger.info(f"Connecting WebSocket for room: {self.room_name}")
        
        # Join room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        recipient_username = data['recipient']

        sender = self.sender
        receiver = User.objects.get(username=recipient_username)

        # Save message to the database
        msg = Message.objects.create(sender=sender, receiver=receiver, content=message)

        # Broadcast the message to the room
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': msg.content,
                'sender': sender.username,
                'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    async def chat_message(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
        }))
