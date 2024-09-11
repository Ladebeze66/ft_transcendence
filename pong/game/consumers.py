import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from .matchmaking import match_maker
from .tournament import tournament_match_maker
import logging

logger = logging.getLogger(__name__)

class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		try:
			await self.accept()
			self.game = None
			logger.info("User connected via WebSocket")
		except Exception as e:
			logger.error(f"Error during WebSocket connection: {str(e)}")

	async def receive(self, text_data):
		try:
			logger.debug(f"Received data: {text_data}")
			data = json.loads(text_data)
			message_type = data.get('type')

			if message_type == 'authenticate':
				await self.authenticate(data.get('token'))
			elif message_type == 'authenticate2':
				await self.authenticate2(data.get('token_1'), data.get('token_2'))
			elif message_type == 'authenticate3':
				await self.authenticate3(data.get('token'))
			elif message_type == 'key_press':
				if self.game:
					await self.game.handle_key_press(self, data.get('key'))
				else:
					await match_maker.handle_key_press(self, data.get('key'))
			else:
				logger.warning(f"Received unknown message type: {message_type}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Unknown message type'}))
		except json.JSONDecodeError as e:
			logger.error(f"JSON decode error: {str(e)} - Data received: {text_data}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON format'}))
		except Exception as e:
			logger.error(f"Error in WebSocket receive: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Internal server error'}))

	async def authenticate(self, token):
		if not token:
			logger.error("Token is None, authentication cannot proceed")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Token is missing'}))
			return
		try:
			user = await self.get_user_from_token(token)
			if user:
				self.user = user
				await self.send(text_data=json.dumps({'type': 'authenticated'}))
				logger.info(f"User {self.user} authenticated")
				await self.join_waiting_room()
			else:
				logger.warning(f"Authentication failed for token: {token}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
		except Exception as e:
			logger.error(f"Error during authentication: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Internal server error'}))

	async def authenticate2(self, token_1, token_2):
		try:
			user = await self.get_user_from_token(token_1)
			if user:
				self.user = user
				await self.send(text_data=json.dumps({'type': 'authenticated'}))
				logger.info(f"User {self.user} authenticated with token_1")

				user2 = await self.get_user_from_token2(token_2)
				if user2:
					self.user2 = user2
					await self.send(text_data=json.dumps({'type': 'authenticated'}))
					logger.info(f"User {self.user2} authenticated with token_2")
					await match_maker.create_game(self, None, True)
				else:
					logger.warning(f"Authentication failed for token_2: {token_2}")
					await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed for user 2'}))
			else:
				logger.warning(f"Authentication failed for token_1: {token_1}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed for user 1'}))
		except Exception as e:
			logger.error(f"Error during dual authentication: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Internal server error'}))

	async def authenticate3(self, token):
		try:
			user = await self.get_user_from_token(token)
			if user:
				self.user = user
				await self.send(text_data=json.dumps({'type': 'authenticated'}))
				logger.info(f"User {self.user} authenticated for tournament")
				await self.join_tournament_waiting_room()
			else:
				logger.warning(f"Authentication failed for token: {token}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
		except Exception as e:
			logger.error(f"Error during tournament authentication: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Internal server error'}))

	@database_sync_to_async
	def get_user_from_token(self, token):
		try:
			user = User.objects.filter(auth_token=token).first()
			logger.debug(f"User found: {user} for token: {token}")
			return user
		except User.DoesNotExist:
			logger.warning(f"User not found for token: {token}")
			return None

	@database_sync_to_async
	def get_user_from_token2(self, token):
		try:
			user2 = User.objects.filter(auth_token=token).first()
			logger.debug(f"User2 found: {user2} for token: {token}")
			return user2
		except User.DoesNotExist:
			logger.warning(f"User not found for token_2: {token}")
			return None

	async def join_waiting_room(self):
		logger.info("Joining waiting room")
		await self.send(text_data=json.dumps({'type': 'waiting_room'}))
		await match_maker.add_player(self)

	async def join_tournament_waiting_room(self):
		logger.info("Joining tournament waiting room")
		await tournament_match_maker.add_player(self)

	async def disconnect(self, close_code):
		try:
			if self.game:
				await self.game.end_game(disconnected_player=self)
			await match_maker.remove_player(self)
			await tournament_match_maker.remove_player(self)
			logger.info(f"User {self.user.username if hasattr(self, 'user') else 'Unknown'} disconnected")
		except Exception as e:
			logger.error(f"Error during WebSocket disconnection: {str(e)}")

	async def set_game(self, game):
		logger.info(f"Setting game: {game}")
		self.game = game
class ChatConsumer(AsyncWebsocketConsumer):
	groups = {}
	blocked_users = {}  # Initialiser la liste des utilisateurs bloqués pour chaque instance de ChatConsumer

	async def connect(self):
		try:
			# Récupérer le nom de la room
			self.room_group_name = self.scope['url_route']['kwargs']['room_name']
		
			# Accepter la connexion WebSocket
			await self.accept()

			logger.info(f"Connexion au WebSocket de chat dans la room {self.room_group_name}")

			# Ajouter l'utilisateur au groupe en mémoire
			if self.room_group_name not in self.groups:
				self.groups[self.room_group_name] = []
			self.groups[self.room_group_name].append(self.channel_name)

		except Exception as e:
			logger.error(f"Erreur lors de la connexion WebSocket: {str(e)}")


	async def disconnect(self, close_code):
		try:
			# Retirer l'utilisateur du groupe en mémoire
			if self.room_group_name in self.groups:
				self.groups[self.room_group_name].remove(self.channel_name)
				if not self.groups[self.room_group_name]:
					del self.groups[self.room_group_name]

			await self.send_group_message(
				self.room_group_name,
				{
					'type': 'chat_message',
					'message': f'{self.user.username if hasattr(self, "user") else "Unknown"} a quitté le chat',
					'username': self.user.username if hasattr(self, "user") else "Unknown",
					'room': self.room_group_name
				}
			)
			logger.info(f"{self.user.username if hasattr(self, 'user') else 'Unknown'} déconnecté du WebSocket de chat dans la room {self.room_group_name}")
		except Exception as e:
			logger.error(f"Erreur lors de la déconnexion WebSocket du chat: {str(e)}")

	async def receive(self, text_data):
		try:
			data = json.loads(text_data)
			message_type = data.get('type')

			username = data.get('username')
			logger.info(f"Message reçu avec username: {username}")
			if not username:
				logger.error(f"Username missing in authenticate message: {data}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Username is missing'}))
				return

			if message_type == 'authenticate':
				await self.authenticate(data.get('token'), username)

			elif message_type == 'chat_message':
				if 'message' not in data or 'username' not in data:
					logger.error(f"Format de message incorrect : {data}")
					await self.send(text_data=json.dumps({'type': 'error', 'message': 'Format de message incorrect'}))
					return

				message = data['message']

				# Logique de blocage : détecter la commande /b
				if message.startswith('/b '):
					block_target = message.split(' ')[1].strip()

					# Vérifier si l'utilisateur cible est dans la room
					if block_target not in self.groups.get(self.room_group_name, []):
						await self.send(text_data=json.dumps({
							'type': 'error', 
							'message': f'Utilisateur {block_target} n\'est pas dans le chat.'
						}))
						return

					# Stocker l'utilisateur bloqué
					if not block_target or block_target == username:
						await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid username for blocking'}))
						return

					if username not in self.blocked_users:
						self.blocked_users[username] = []
					self.blocked_users[username].append(block_target)
					logger.info(f"{username} a bloqué {block_target}")
					await self.send(text_data=json.dumps({'type': 'info', 'message': f'You have blocked {block_target}'}))
					return

				# Logique d'invitation à un quick match : détecter la commande /i
				elif message.startswith('/i '):
					invite_target = message.split(' ')[1].strip()

					# Vérifier si l'utilisateur cible est dans la room
					if invite_target not in self.groups.get(self.room_group_name, []):
						await self.send(text_data=json.dumps({
							'type': 'error', 
							'message': f'Utilisateur {invite_target} n\'est pas dans le chat.'
						}))
						return

					if not invite_target or invite_target == username:
						await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid username for invitation'}))
						return

					# Envoi de l'invitation au joueur cible
					await self.send_invitation(invite_target, username)
					return

				# Si l'expéditeur est bloqué, ignorer le message
				if username in self.blocked_users.get(self.room_group_name, []):
					logger.info(f"Message de {username} bloqué pour {self.room_group_name}")
					return

				# Envoyer le message à tous les autres utilisateurs de la room
				await self.send_group_message(
					self.room_group_name,
					{
						'type': 'chat_message',
						'message': message,
						'username': username,
						'room': self.room_group_name
					}
				)
			else:
				logger.warning(f"Unhandled message type: {message_type}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Unhandled message type'}))
		except json.JSONDecodeError as e:
			logger.error(f"Erreur de décodage JSON : {str(e)} - Données reçues : {text_data}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Format JSON invalide'}))
		except Exception as e:
			logger.error(f"Erreur lors de la réception du message du chat: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Erreur interne du serveur'}))


	async def send_invitation(self, invite_target, inviter):
		# Envoie l'invitation à l'utilisateur cible pour un quick match
		try:
			await self.send(text_data=json.dumps({
				'type': 'invitation',
				'message': f"{inviter} t'invite à un quick match. Acceptes-tu ? (oui/non)",
				'inviter': inviter,
				'invitee': invite_target
			}))
			logger.info(f"Invitation envoyée de {inviter} à {invite_target} pour un quick match.")
		except Exception as e:
			logger.error(f"Erreur lors de l'envoi de l'invitation: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Erreur lors de l\'envoi de l\'invitation'}))

	async def handle_quickmatch_response(self, response, invitee, inviter):
		try:
			if response.lower() == "oui":
				logger.info(f"{invitee} accepte l'invitation de {inviter} pour un quick match.")
			
				# Logique pour démarrer le quick match
				await self.start_quickmatch(invitee, inviter)
			
				# Informer tous les utilisateurs du chat de l'acceptation
				await self.send_group_message(
					self.room_group_name,
					{
						'type': 'chat_message',
						'message': f"{invitee} a accepté l'invitation de {inviter} pour un quick match.",
						'username': invitee,
						'room': self.room_group_name
					}
				)
			else:
				logger.info(f"{invitee} a refusé l'invitation de {inviter}")
			
				# Informer que l'invitation a été refusée et retourner au chat normal
				await self.send_group_message(
					self.room_group_name,
					{
						'type': 'chat_message',
						'message': f"{invitee} a refusé l'invitation de {inviter}.",
						'username': invitee,
						'room': self.room_group_name
					}
				)
			
				await self.send(text_data=json.dumps({'type': 'info', 'message': 'Invitation refusée, retour au chat normal.'}))
	
		except Exception as e:
			logger.error(f"Erreur lors du traitement de la réponse au quick match: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Erreur lors du traitement de la réponse à l\'invitation.'}))


	async def start_quickmatch(self, invitee, inviter):
		try:
			# Logique pour démarrer le quick match entre invitee et inviter
			logger.info(f"Démarrage du quick match entre {invitee} et {inviter}")
		
			# Informer tous les utilisateurs de la room que le quick match démarre
			await self.send_group_message(
				self.room_group_name,
				{
					'type': 'chat_message',
					'message': f"Démarrage du quick match entre {invitee} et {inviter}.",
					'username': inviter,
					'room': self.room_group_name
				}
			)

			# Exécuter la logique propre au démarrage d'un quick match (en fonction de ta logique métier)
			# ...

			# Informer les utilisateurs concernés
			await self.send(text_data=json.dumps({
				'type': 'info',
				'message': f"Le quick match entre {invitee} et {inviter} a démarré."
			}))
		
		except Exception as e:
			logger.error(f"Erreur lors du démarrage du quick match: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Erreur lors du démarrage du quick match.'}))

	async def authenticate(self, token, username):
		if not token:
			logger.error("Token is None, authentication cannot proceed")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Token is missing'}))
			return
		try:
			user = await self.get_user_from_token(token)
			if user:
				self.user = user
				logger.info(f"User {username} authenticated successfully")
			
				# Envoyer un message d'authentification réussie au client
				await self.send(text_data=json.dumps({'type': 'authenticated', 'username': username}))

				# Envoyer le message de bienvenue après l'authentification réussie
				await self.send_group_message(
					self.room_group_name,
					{
						'username': username,
						'room': self.room_group_name,
						'type': 'chat_message',
						'message': f' a rejoint le chat {self.room_group_name}',
					}
				)
			else:
				logger.warning(f"Authentication failed for token: {token}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
		except Exception as e:
			logger.error(f"Error during authentication: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Internal server error'}))

	@sync_to_async
	def get_user_from_token(self, token):
		try:
			user = User.objects.filter(auth_token=token).first()
			if user:
				logger.debug(f"User found: {user} for token: {token}")
			else:
				logger.warning(f"No user found for token: {token}")
			return user
		except Exception as e:
			logger.error(f"Error while retrieving user for token {token}: {str(e)}")
			return None

	async def send_group_message(self, room_group_name, message_data):
		# Envoie un message à tous les utilisateurs du groupe spécifié
		try:
			await self.channel_layer.group_send(
				room_group_name,
				{
					'type': 'chat_message',  # Indique que c'est un message de chat
					'message': message_data['message'],
					'username': message_data.get('username', 'Anonymous'),  # Définit 'Anonymous' si username est manquant
					'room': room_group_name
				}
			)
			logger.info(f"Message envoyé au groupe {room_group_name}: {message_data['message']}")
		except Exception as e:
			logger.error(f"Erreur lors de l'envoi du message au groupe {room_group_name}: {str(e)}")

	async def chat_message(self, event):
		# Extraire les informations de l'événement
		message = event['message']
		username = event.get('username', 'Anonyme')  # Utilise 'Anonyme' si le nom d'utilisateur est manquant
		room = event.get('room', 'unknown')  # Utilise 'unknown' si la room est manquante

		# Log pour vérifier les informations avant envoi
		logger.info(f"Envoi du message '{message}' de l'utilisateur '{username}' dans la room '{room}'")

		try:
			# Envoyer le message au WebSocket
			await self.send(text_data=json.dumps({
				'type': 'chat_message',
				'message': f'{username}: {message}',  # Format du message affiché aux utilisateurs
				'room': room
			}))
		except Exception as e:
			logger.error(f"Erreur lors de l'envoi du message de chat : {str(e)}")
