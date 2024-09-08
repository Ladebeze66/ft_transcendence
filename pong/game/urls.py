# /pong/game/urls.py

from django.urls import path, include
from . import views
#from rest_framework.routers import DefaultRouter
from .views import match_list_json, player_list_json, tournoi_list_json

urlpatterns = [
    path('', views.index, name='index'),
    path('check_user_exists/', views.check_user_exists, name='check_user_exists'),
    path('register_user/', views.register_user, name='register_user'),
    path('authenticate_user/', views.authenticate_user, name='authenticate_user'),
    path('web3/', views.read_data, name='read_data'),
    path('api/match_list/', match_list_json, name='match_list_json'),
    path('api/player_list/', player_list_json, name='player_list_json'),
    path('api/tournoi_list/', tournoi_list_json, name='tournoi_list_json')
]
