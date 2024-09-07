# pong/middleware.py

from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
import logging

logger = logging.getLogger(__name__)

class CustomAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Log the scope for debugging
        logger.info(f"Scope before authentication: {scope}")

        # Call the inner application
        close_old_connections()

        scope['user'] = scope.get('user', AnonymousUser())
        if scope['user'].is_authenticated:
            logger.info(f"User authenticated: {scope['user']}")
        else:
            logger.warning("No authenticated user found")

        return await super().__call__(scope, receive, send)
