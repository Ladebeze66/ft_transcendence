# pong/game/chat_consumer.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Vérifier si l'utilisateur est authentifié
        if self.scope["user"].is_authenticated:
            await self.accept()
            self.room_group_name = 'chat_room'
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = self.scope["user"].username

        # Envoyer le message à tous les clients connectés
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Envoyer le message au WebSocket client
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))
