# /pong/game/routing.py
from django.urls import re_path
from . import consumers
import logging

logger = logging.getLogger(__name__)

logger.debug("Configuring WebSocket routing patterns for game")

websocket_urlpatterns = [
    re_path(r'ws/game/$', consumers.GameConsumer.as_asgi(), name='game_ws'),
]

logger.info("WebSocket routing patterns for game configured successfully")
