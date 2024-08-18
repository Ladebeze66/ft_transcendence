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

def tournoi_list_json(request):
    # Récupère tous les joueurs
    tournois = Tournoi.objects.all()
    
    # Crée un dictionnaire avec les informations des joueurs
    data = {
        'tournois': list(tournois.values(
            'id', 'name', 'nbr_player', 'date', 'winner'
        ))
    }
    
    # Renvoie les données en JSON
    return JsonResponse(data)


####################### THEOUCHE PART ############################



####################### jcheca PART ############################

from web3 import Web3

provider = Web3.HTTPProvider("https://sepolia.infura.io/v3/60e51df7c97c4f4c8ab41605a4eb9907")
web3 = Web3(provider)
eth_gas_price = web3.eth.gas_price/1000000000
print(eth_gas_price)

contract_address = "0x078D04Eb6fb97Cd863361FC86000647DC876441B"
contract_abi = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"uint256","name":"_timecode","type":"uint256"},{"internalType":"uint256","name":"_participantCount","type":"uint256"},{"internalType":"string[]","name":"_playerPseudonyms","type":"string[]"},{"internalType":"string[]","name":"_finalOrder","type":"string[]"}],"name":"addTournament","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getAllTournaments","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"string","name":"name","type":"string"},{"internalType":"uint256","name":"timecode","type":"uint256"},{"internalType":"uint256","name":"participantCount","type":"uint256"},{"internalType":"string[]","name":"playerPseudonyms","type":"string[]"},{"internalType":"string[]","name":"finalOrder","type":"string[]"}],"internalType":"struct PongTournament.Tournament[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_id","type":"uint256"}],"name":"getTournament","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"string","name":"name","type":"string"},{"internalType":"uint256","name":"timecode","type":"uint256"},{"internalType":"uint256","name":"participantCount","type":"uint256"},{"internalType":"string[]","name":"playerPseudonyms","type":"string[]"},{"internalType":"string[]","name":"finalOrder","type":"string[]"}],"internalType":"struct PongTournament.Tournament","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"tournamentCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"tournaments","outputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"string","name":"name","type":"string"},{"internalType":"uint256","name":"timecode","type":"uint256"},{"internalType":"uint256","name":"participantCount","type":"uint256"}],"stateMutability":"view","type":"function"}]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def read_data(request):
    # Créer une instance du contrat

    # Appeler une fonction du contrat pour obtenir tous les tournois
    tournaments = contract.functions.getAllTournaments().call()

    # Afficher les résultats
    json_data = []
    for tournament in tournaments:
        tournament_data = []
        for item in tournament:
            print(f"{item}")
            tournament_data.append(item)
        json_data.append(tournament_data)

    # Retourner le JSON comme réponse HTTP
        # print(f"Tournament ID: {tournament[0]}")
        # print(f"Name: {tournament[1]}")
        # print(f"Timecode: {tournament[2]}")
        # print(f"Participant Count: {tournament[3]}")
        # print(f"Player Pseudonyms: {', '.join(tournament[4])}")
        # print(f"Final Order: {', '.join(tournament[5])}")
    print("-----------------------------")
    return JsonResponse(json_data, safe=False)
        

def write_data(request):
    # addTournament(string,uint256,uint256,string[],string[])

    # # Configuration de la transaction pour la fonction store
    # account = "0x66CeBE2A1F7dae0F6AdBAad2c15A56A9121abfEf"
    # private_key = "beb16ee3434ec5abec8b799549846cc04443c967b8d3643b943e2e969e7d25be"

    # nonce = web3.eth.get_transaction_count(account)
    # transaction = contract.functions.addTournament("test",1721830559,6,["aaudeber", "tlorne", "ocassany", "yestello", "jcheca", "toto"],["toto", "jcheca", "yestello", "tlorne", "ocassany", "aaudeber"]).build_transaction({
    #     'chainId': 11155111,  # ID de la chaîne Sepolia
    #     'gas': 2000000,
    #     'gasPrice': web3.to_wei(eth_gas_price, 'gwei'),
    #     'nonce': nonce
    # })

    # # Signature de la transaction
    # signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

    # # Envoi de la transaction
    # tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # print("Transaction hash:", web3.to_hex(tx_hash))

    # # Attente de la confirmation de la transaction
    # tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    # print("Transaction receipt:", tx_receipt)
    print("-----------------------------")

