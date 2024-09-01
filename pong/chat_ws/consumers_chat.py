
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat'
        self.user = self.scope["user"]
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': f'{self.user.username} has joined the chat'
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': f'{self.user.username} has left the chat'
        })

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': f'{username}: {message}'
        })

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))