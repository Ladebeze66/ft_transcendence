# pong/game/routing.py

from django.urls import re_path
from . import consumers
from . import chat_consumer

websocket_urlpatterns = [
    re_path(r'ws/game/$', consumers.GameConsumer.as_asgi()),
    re_path(r'ws/chat/$', chat_consumer.ChatConsumer.as_asgi()),  # Ajout de la route pour le chat
]
