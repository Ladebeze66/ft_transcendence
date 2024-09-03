import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_group_name = 'chat'
            self.user = self.scope["user"]
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info(f"{self.user.username} connected to chat WebSocket")
            # Envoyer le message de connexion au groupe avec le format attendu
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message',
                'message': f'{self.user.username} has joined the chat',
                'username': 'System'  # Utilisation d'un nom d'utilisateur 'System' pour ces messages
            })
        except Exception as e:
            logger.error(f"Error during chat WebSocket connection: {str(e)}")

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message',
                'message': f'{self.user.username} has left the chat',
                'username': 'System'  # Utilisation d'un nom d'utilisateur 'System' pour ces messages
            })
            logger.info(f"{self.user.username} disconnected from chat WebSocket")
        except Exception as e:
            logger.error(f"Error during chat WebSocket disconnection: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message')
            username = data.get('username')

            if message and username:
                logger.debug(f"Received message from {username}: {message}")
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'chat_message',
                    'message': f'{username}: {message}'
                })
            else:
                logger.warning("Missing 'message' or 'username' in received data")
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid message format'}))
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in chat receive: {str(e)} - Data received: {text_data}")
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON format'}))
        except Exception as e:
            logger.error(f"Error during chat message receive: {str(e)}")
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Internal server error'}))

    async def chat_message(self, event):
        try:
            message = event['message']
            await self.send(text_data=json.dumps({'message': message}))
            logger.debug(f"Broadcasting chat message: {message}")
        except Exception as e:
            logger.error(f"Error during chat message broadcast: {str(e)}")