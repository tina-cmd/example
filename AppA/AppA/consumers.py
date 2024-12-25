# appA/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from cryptography.fernet import Fernet
from django.conf import settings
from .models import Message
from django.contrib.auth.models import User

# Encryption cipher
cipher = Fernet(settings.ENCRYPTION_KEY)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json['content']
        sender_username = text_data_json['sender']

        # Encrypt the message content
        encrypted_content = cipher.encrypt(content.encode()).decode()

        # Save the message to the database
        sender = User.objects.get(username=sender_username)
        message = Message(sender=sender, recipient=sender, content=content, encrypted_content=encrypted_content)
        message.save()

        # Broadcast the message to the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': sender.username,
                'content': encrypted_content,  # Send encrypted content
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        content = event['content']
        sender = event['sender']

        # Decrypt the message content before sending it to the WebSocket
        decrypted_content = cipher.decrypt(content.encode()).decode()

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender': sender,
            'content': decrypted_content,
        }))
