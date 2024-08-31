from django.urls import re_path
from .consumers import GameConsumer
from pong.chat_ws import consumers as chat_consumers

websocket_urlpatterns = [
    re_path(r'ws/game/$', GameConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', chat_consumers.ChatConsumer.as_asgi()),  # Route ajoutée pour le chat
]
