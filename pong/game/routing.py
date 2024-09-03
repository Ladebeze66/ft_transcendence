# /pong/game/routing.py
from django.urls import re_path
from . import consumerschat
from . import consumers
import logging

logger = logging.getLogger(__name__)

logger.debug("Configuring WebSocket routing patterns")

websocket_urlpatterns = [
    re_path(r'ws/game/$', consumers.GameConsumer.as_asgi(), name='game_ws'),
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi(), name='chat_ws'),
]

logger.info("WebSocket routing patterns configured successfully")
