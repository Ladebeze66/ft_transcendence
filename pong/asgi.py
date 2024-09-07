# /pong/asgi.py

"""
ASGI config for pong project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

# pong/asgi.py

import os
import django
import logging

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from pong.middleware import CustomAuthMiddleware
import pong.game.routing
import pong.game.routingchat

# Configuration du logger
logger = logging.getLogger(__name__)

# Définir la variable d'environnement pour les paramètres Django
logger.debug("Setting default DJANGO_SETTINGS_MODULE to 'pong.settings'")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong.settings')

# Initialiser Django
logger.debug("Initializing Django setup")
django.setup()

# Configurer le routeur de protocoles
logger.debug("Configuring ProtocolTypeRouter")
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
        URLRouter(
            pong.game.routing.websocket_urlpatterns,
            AuthMiddlewareStack()
        ),
        URLRouter(
            pong.game.routingchat.websocket_urlpatterns,
            CustomAuthMiddleware()
        ),
    ]),
})

logger.info("ASGI application configurée et prête à accepter les connexions")
