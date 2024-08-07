# /pong/game/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from .matchmaking import match_maker

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.game = None
        print("User connected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'authenticate':
            await self.authenticate(data['token'])
        elif data['type'] == 'key_press':
            if self.game:
                await self.game.handle_key_press(self, data['key'])
            else:
                await match_maker.handle_key_press(self, data['key'])

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

    async def disconnect(self, close_code):
        if self.game:
            await self.game.end_game(disconnected_player=self)
        await match_maker.remove_player(self)
        print(f"User {self.user.username if hasattr(self, 'user') else 'Unknown'} disconnected")

    async def set_game(self, game):
        self.game = game
