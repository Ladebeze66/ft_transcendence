# /pong/game/views.py

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .models import Player, Tournoi, Match
from .utils import create_player, create_tournoi, create_match
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.db import transaction, IntegrityError

import json
import uuid
import logging

logger = logging.getLogger(__name__)

def index(request):
    logger.info("Accessing index view")
    return render(request, 'index.html')

@csrf_exempt
def check_user_exists(request):
    if request.method == 'POST':
        logger.info("POST request received for checking user existence")
        data = json.loads(request.body)
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            logger.info(f"User {username} exists")
            return JsonResponse({'exists': True})
        logger.info(f"User {username} does not exist")
        return JsonResponse({'exists': False})
    logger.warning("Invalid request method for check_user_exists")
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            logger.info("Received POST request for user registration")
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            logger.info(f"Attempting to register user: {username}")

            if not username or not password:
                logger.warning("Username or password not provided")
                return JsonResponse({'registered': False, 'error': 'Username and password are required'}, status=400)

            with transaction.atomic():
                user_exists = User.objects.select_for_update().filter(username=username).exists()

                if user_exists:
                    logger.warning(f"User {username} already exists")
                    return JsonResponse({'registered': False, 'error': 'User already exists'}, status=409)

                user = User.objects.create_user(username=username, password=password)
                token = get_or_create_token(user)
                logger.info(f"User {username} registered successfully")
                return JsonResponse({'registered': True, 'token': token})

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        except IntegrityError:
            logger.error(f"IntegrityError: User {username} already exists")
            return JsonResponse({'registered': False, 'error': 'User already exists'}, status=409)

        except Exception as e:
            logger.error(f"Error in register_user: {str(e)}")
            return JsonResponse({'error': f'Internal Server Error: {str(e)}'}, status=500)

    logger.warning("Invalid request method for register_user")
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_or_create_token(user):
    logger.info(f"Generating or retrieving token for user: {user.username}")
    if not user.auth_token:
        while True:
            token = str(uuid.uuid4())
            if not User.objects.filter(auth_token=token).exists():
                user.auth_token = token
                user.save()
                logger.info(f"Token generated for user {user.username}: {token}")
                break
    return user.auth_token

@csrf_exempt
def authenticate_user(request):
    if request.method == 'POST':
        try:
            logger.info("Received POST request for user authentication")
            data = json.loads(request.body)
            username = data.get('username', '')
            password = data.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                token = get_or_create_token(user)
                logger.info(f"User {username} authenticated successfully")
                return JsonResponse({'authenticated': True, 'token': token, 'user_id': user.id})
            else:
                logger.warning(f"Authentication failed for user {username}")
                return JsonResponse({'authenticated': False}, status=401)
        except Exception as e:
            logger.error(f"Error in authenticate_user: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        logger.warning("Invalid request method for authenticate_user")
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def match_list_json(request):
    logger.info("Fetching match list")
    matches = Match.objects.all()
    data = {
        'matches': list(matches.values(
            'id', 'player1__name', 'player2__name', 'score_player1', 'score_player2',
            'winner__name', 'nbr_ball_touch_p1', 'nbr_ball_touch_p2', 'duration', 'date',
            'is_tournoi', 'tournoi__name'
        ))
    }
    logger.info(f"Match list fetched successfully: {len(data['matches'])} matches found")
    return JsonResponse(data)

def player_list_json(request):
    logger.info("Fetching player list")
    players = Player.objects.all()

    data = {
        'players': list(players.values(
            'id', 'name', 'total_match', 'total_win', 'p_win',
            'm_score_match', 'm_score_adv_match', 'best_score',
            'm_nbr_ball_touch', 'total_duration', 'm_duration',
            'num_participated_tournaments', 'num_won_tournaments'
        ))
    }
    logger.info(f"Player list fetched successfully: {len(data['players'])} players found")
    return JsonResponse(data)

def tournoi_list_json(request):
    logger.info("Fetching tournoi list")
    tournois = Tournoi.objects.all()

    data = {
        'tournois': list(tournois.values(
            'id', 'name', 'nbr_player', 'date', 'winner'
        ))
    }
    logger.info(f"Tournoi list fetched successfully: {len(data['tournois'])} tournois found")
    return JsonResponse(data)

def tournoi_list_json(request):
    tournois = Tournoi.objects.all()

    data = {
        'tournois': list(tournois.values(
            'id', 'name', 'nbr_player', 'date', 'winner'
        ))
    }
    return JsonResponse(data)

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
