# /pong/chat/routing.py
from django.urls import re_path
from . import consumers
import logging

logger = logging.getLogger(__name__)

logger.debug("Configuring WebSocket routing patterns for chat")

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi(), name='chat_ws'),
]

logger.info("WebSocket routing patterns for chat configured successfully")