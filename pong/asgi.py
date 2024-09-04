# /pong/asgi.py

"""
ASGI config for pong project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
from redis import Redis, ConnectionError
import logging

logger = logging.getLogger(__name__)

# Vérification de la connexion à Redis
try:
    redis_instance = Redis(host='redis', port=6379)
    if redis_instance.ping():
        logger.info("Connexion à Redis réussie")
except ConnectionError as e:
    logger.error(f"Échec de la connexion à Redis: {e}")
    # Vous pouvez ici décider de stopper l'exécution ou de continuer avec une configuration alternative

logger.debug("Setting default DJANGO_SETTINGS_MODULE to 'pong.settings'")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong.settings')

logger.debug("Initializing Django setup")
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import pong.game.routing

logger.debug("Configuring ProtocolTypeRouter")
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            pong.game.routing.websocket_urlpatterns
        )
    ),
})

logger.info("ASGI application configurée et prête à accepter les connexions")
