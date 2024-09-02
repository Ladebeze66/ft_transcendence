# /pong/game/urls.py

from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import match_list_json, player_list_json, tournoi_list_json
import logging

logger = logging.getLogger(__name__)

# Add logs to indicate which URL patterns are being accessed
def log_url_access(view_func):
    def wrapper(*args, **kwargs):
        logger.info(f"Accessing URL: {view_func.__name__}")
        return view_func(*args, **kwargs)
    return wrapper

urlpatterns = [
    path('', log_url_access(views.index), name='index'),
    path('check_user_exists/', log_url_access(views.check_user_exists), name='check_user_exists'),
    path('register_user/', log_url_access(views.register_user), name='register_user'),
    path('authenticate_user/', log_url_access(views.authenticate_user), name='authenticate_user'),
    path('web3/', log_url_access(views.read_data), name='read_data'),
    path('api/match_list/', log_url_access(match_list_json), name='match_list_json'),
    path('api/player_list/', log_url_access(player_list_json), name='player_list_json'),
    path('api/tournoi_list/', log_url_access(tournoi_list_json), name='tournoi_list_json')
]
