# /pong/game/consumers.py

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from pong.game.models import ChatRoom, ChatMessage, Player
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.roomid = self.scope['url_route']['kwargs']['roomid']
        self.room_name = f"chat-{self.roomid}"
        self.registered = False

        # Check if roomid exists
        try:
            self.chatObject = await sync_to_async(ChatRoom.objects.get)(id=self.roomid)
        except ChatRoom.DoesNotExist:
            await self.disconnect_when_connecting()
            return

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_name, self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        if content.get('command') == 'join':
            await self.new_connection(content['username'])
        elif content.get('command') == 'message':
            await self.handle_message(content['message'])

    async def new_connection(self, username):
        try:
            userObject = await sync_to_async(Player.objects.get)(name=username)
        except Player.DoesNotExist:
            await self.send_json({
                "command": "error",
                "message": "User not found."
            })
            return await self.close()

        if not await sync_to_async(self.check_membership)(userObject):
            await self.send_json({
                "command": "error",
                "message": "You aren't invited!"
            })
            return await self.close()

        self.username = username
        self.userObject = userObject
        self.registered = True

        await self.channel_layer.group_add(
            self.room_name, self.channel_name
        )
        await self.send_status()

    def check_membership(self, userObject):
        return self.chatObject.owner == userObject or userObject in self.chatObject.members.all()

    async def send_status(self):
        await self.send_json({
            "command": "details",
            "details": await sync_to_async(self.get_serialized_data)()
        })

    def get_serialized_data(self):
        return {
            "name": self.chatObject.name,
            "owner": self.chatObject.owner.name,
            "members": [member.name for member in self.chatObject.members.all()],
            "messages": [
                {
                    "sender": message.sender.name,
                    "message": message.message,
                    "timestamp": message.timestamp.isoformat()
                }
                for message in self.chatObject.messages.all()
            ]
        }

    async def handle_message(self, message):
        if not self.registered:
            await self.send_json({
                "command": "error",
                "message": "You are not registered in the room."
            })
            return

        chat_message = await sync_to_async(ChatMessage.objects.create)(
            room=self.chatObject,
            sender=self.userObject,
            message=message
        )

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": {
                    "sender": chat_message.sender.name,
                    "message": chat_message.message,
                    "timestamp": chat_message.timestamp.isoformat()
                }
            }
        )

    async def chat_message(self, event):
        await self.send_json({
            "command": "message",
            "message": event["message"]
        })

    async def disconnect_when_connecting(self):
        await self.accept()
        await self.close()