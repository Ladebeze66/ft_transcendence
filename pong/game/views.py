# /pong/game/views.py

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

from django.core.exceptions import ObjectDoesNotExist
from .models import Player, Tournoi, Match
from .utils import create_player, create_tournoi, create_match
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
""" from .serializers import MatchSerializer """
from rest_framework import viewsets

import json
import uuid

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password)
            token = get_or_create_token(user)
            return JsonResponse({'registered': True, 'token': token})
        return JsonResponse({'registered': False, 'error': 'User already exists'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def check_user_exists(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'exists': True})
        return JsonResponse({'exists': False})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def authenticate_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '')
            password = data.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                token = get_or_create_token(user)
                return JsonResponse({'authenticated': True, 'token': token, 'user_id': user.id})
            else:
                return JsonResponse({'authenticated': False}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_or_create_token(user):
    if not user.auth_token:
        while True:
            token = str(uuid.uuid4())
            if not User.objects.filter(auth_token=token).exists():
                user.auth_token = token
                user.save()
                break
    return user.auth_token


####################### THEOUCHE PART ############################

def player_list(request):
    players = Player.objects.all()
    return render(request, 'pong/player_list.html', {'players': players})

def match_list(request):
    matches = Match.objects.select_related('player1', 'player2', 'winner', 'tournoi').all()
    return render(request, 'pong/match_list.html', {'matches': matches})

def tournoi_list(request):
    tournois = Tournoi.objects.select_related('winner').all()
    return render(request, 'pong/tournoi_list.html', {'tournois': tournois})

from django.http import JsonResponse

def match_list_json(request):
    matches = Match.objects.all()
    data = {
        'matches': list(matches.values(
            'id', 'player1__name', 'player2__name', 'score_player1', 'score_player2',
            'winner__name', 'nbr_ball_touch_p1', 'nbr_ball_touch_p2', 'duration', 'date',
            'is_tournoi', 'tournoi__name'
        ))
    }
    return JsonResponse(data)

def player_list_json(request):
    # Récupère tous les joueurs
    players = Player.objects.all()
    
    # Crée un dictionnaire avec les informations des joueurs
    data = {
        'players': list(players.values(
            'id', 'name', 'total_match', 'total_win', 'p_win',
            'm_score_match', 'm_score_adv_match', 'best_score',
            'm_nbr_ball_touch', 'total_duration', 'm_duration',
            'num_participated_tournaments', 'num_won_tournaments'
        ))
    }
    
    # Renvoie les données en JSON
    return JsonResponse(data)


####################### THEOUCHE PART ############################
