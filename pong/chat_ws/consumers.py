from channels.generic.websocket import AsyncJsonWebsocketConsumer
from pong.game.models import ChatRoom, ChatMessage, Player
from asgiref.sync import sync_to_async
import datetime

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.roomid = self.scope['url_route']['kwargs']['roomid']
        self.room_name = f"chat-{self.roomid}"
        self.registered = False

        # Check if roomid exists
        try:
            self.chatObject = await sync_to_async(ChatRoom.objects.get)(roomid=self.roomid)
        except Exception as e:
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

    async def new_connection(self, username):
        try:
            userObject = await sync_to_async(Player.objects.get)(username=username)
        except Exception as e:
            await self.send_json({
                "command": "error",
                "message": "User not found."
            })
            return await self.close()

        if (await sync_to_async(self.check)(userObject)):
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

    def check(self, userObject):
        return (self.chatObject.owner != userObject and userObject not in self.chatObject.members.all())

    async def send_status(self):
        await self.send_json({
            "command": "details",
            "details": await sync_to_async(self.get_serialized_data)()
        })

    def get_serialized_data(self):
        return ChatRoomSerializer(self.chatObject).data

    async def disconnect_when_connecting(self):
        await self.accept()
        await self.close()
