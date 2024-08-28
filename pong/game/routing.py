# /pong/game/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/$', consumers.GameConsumer.as_asgi()),
	re_path(r'ws/chat/(?<room_name>\w+)/$', consumers.GameConsumer.as_asgi()), # Route pour le chat
]
