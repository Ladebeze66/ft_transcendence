# /pong/game/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from .matchmaking import match_maker
from django.utils import timezone  # Pour gérer les dates et heures
from .models import ChatMessage  # Pour utiliser le modèle ChatMessage que vous avez créé

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.game = None
        self.room_name = None #ajout pour le chat
        print("User connected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'chat_message':#ajout chat
            await self.handle_chat_message(data)#ajout chat
        if data['type'] == 'authenticate':
            await self.authenticate(data['token'])
        elif data['type'] == 'authenticate2':
            await self.authenticate2(data['token_1'], data['token_2'])
        elif data['type'] == 'key_press':
            if self.game:
                await self.game.handle_key_press(self, data['key'])
            else:
                await match_maker.handle_key_press(self, data['key'])
#//////// CHAT ///////////
    async def handle_chat_message(self, data):
        message = data['message']
        room = data['room']
        user = self.user

        # Enregistrez le message dans la base de données
        await self.save_chat_message(user, room, message)

        # Envoyez le message à tous les utilisateurs du salon
        await self.channel_layer.group_send(
            room,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.username,
                'timestamp': str(timezone.now())
            }
        )

    @database_sync_to_async
    def save_chat_message(self, user, room, message):
        return ChatMessage.objects.create(user=user, room=room, content=message)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
#//////// CHAT ///////////

    async def authenticate(self, token):
        user = await self.get_user_from_token(token)
        if user:
            self.user = user
            await self.send(text_data=json.dumps({'type': 'authenticated'}))
            print(f"User {self.user} authenticated")
            await self.join_waiting_room()
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
            print("Authentication failed")

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            user = User.objects.filter(auth_token=token).first()
            return user
        except User.DoesNotExist:
            return None

    async def join_waiting_room(self):
        await self.send(text_data=json.dumps({'type': 'waiting_room'}))
        await match_maker.add_player(self)

    async def authenticate2(self, token, token2):
        user = await self.get_user_from_token(token)
        if user:
            self.user = user
            await self.send(text_data=json.dumps({'type': 'authenticated'}))
            print(f"User {self.user} authenticated")
            user2 = await self.get_user_from_token2(token2)
            if user2:
                self.user2 = user2
                await self.send(text_data=json.dumps({'type': 'authenticated'}))
                print(f"User {self.user2} authenticated")
                await match_maker.create_game(self, None, True)
            else:
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
                print("Authentication failed")
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
            print("Authentication failed")

    @database_sync_to_async
    def get_user_from_token2(self, token):
        try:
            user2 = User.objects.filter(auth_token=token).first()
            return user2
        except User.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        if self.game:
            await self.game.end_game(disconnected_player=self)
        await match_maker.remove_player(self)
        print(f"User {self.user.username if hasattr(self, 'user') else 'Unknown'} disconnected")

    async def set_game(self, game):
        self.game = game
