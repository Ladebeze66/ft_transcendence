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
###############################CHAT############################################
class ChatConsumer(AsyncWebsocketConsumer):
	groups = {}

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

			logger.info(f"User {self.channel_name} added to group {self.room_group_name}")

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
			username = data.get('username').strip().lower()  # Normalisation du nom d'utilisateur

			# Log pour vérifier que le username est bien reçu
			logger.info(f"Message reçu avec username: {username}")
			if not username:
				logger.error(f"Username missing in message: {data}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Username is missing'}))
				return

			# Gestion des types de messages
			if message_type == 'authenticate':
				await self.authenticate(data.get('token'), username)

			elif message_type == 'chat_message':
				if 'message' not in data:
					logger.error(f"Format de message incorrect : {data}")
					await self.send(text_data=json.dumps({'type': 'error', 'message': 'Format de message incorrect'}))
					return

				message = data['message']

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

			# Gestion de la commande /b pour bloquer un utilisateur
			elif message_type == 'block_user':
				target_user = data.get('target_user').strip().lower()
				if target_user == username:
					await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot block yourself'}))
				else:
					await self.handle_block_user(data)

			# Gestion de la commande /i pour inviter un utilisateur
			elif message_type == 'invite_user':
				target_user = data.get('target_user').strip().lower()
				if target_user == username:
					await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot invite yourself'}))
				else:
					await self.handle_invite_user(data)

			else:
				logger.warning(f"Unhandled message type: {message_type}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Unhandled message type'}))

		except json.JSONDecodeError as e:
			logger.error(f"Erreur de décodage JSON : {str(e)} - Données reçues : {text_data}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Format JSON invalide'}))
		except Exception as e:
			logger.error(f"Erreur lors de la réception du message du chat: {str(e)}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Erreur interne du serveur'}))

	async def handle_block_user(self, data):
		username = data['username'].strip().lower()  # Normalisation du nom d'utilisateur
		target_user = data['target_user'].strip().lower()

		# Utiliser self.room_group_name pour vérifier que l'utilisateur ciblé est bien dans la bonne room
		if target_user not in self.groups.get(self.room_group_name, []):
			logger.error(f"Target user {target_user} does not exist in room {self.room_group_name}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': f'Target user {target_user} not found in room {self.room_group_name}'}))
			return

		logger.info(f"Block request: {username} wants to block {target_user} in room {self.room_group_name}")

		if target_user == username:
			logger.warning(f"Block attempt failed: {username} tried to block themselves")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot block yourself'}))
		else:
			logger.info(f"{username} successfully blocked {target_user}")
			await self.send(text_data=json.dumps({'type': 'success', 'message': f'You have blocked {target_user} in room {self.room_group_name}'}))

	async def handle_invite_user(self, data):
		username = data['username'].strip().lower() 
		target_user = data['target_user'].strip().lower()

		# Utiliser self.room_group_name pour inviter l'utilisateur dans la room active
		room = self.room_group_name

		# Vérification que le joueur à inviter est dans la room
		if target_user not in self.groups.get(room, []):
			logger.error(f"Target user {target_user} does not exist in room {room}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': f'Target user {target_user} not found in room {room}'}))
			return

		logger.info(f"Invitation request: {username} wants to invite {target_user} to a quick match in room {room}")

		if target_user == username:
			logger.warning(f"Invite attempt failed: {username} tried to invite themselves")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot invite yourself'}))
		else:
			logger.info(f"{username} successfully sent an invitation to {target_user} in room {room}")
			await self.send_group_message(room, {
				'type': 'invite',
				'message': f'{username} invited {target_user} to a quick match',
				'username': username,
				'target_user': target_user
			})
			await self.send(text_data=json.dumps({'type': 'success', 'message': f'Invitation sent to {target_user} in room {room}'}))


	async def authenticate(self, token, username):
		if not token:
			logger.error("Token is None, authentication cannot proceed")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Token is missing'}))
			return
		try:
			user = await self.get_user_from_token(token)
			if user:
				self.user = user
				logger.info(f"User {username} authenticated successfully with token: {token}")
			
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
			logger.debug(f"User found: {user} for token: {token}")
			return user
		except User.DoesNotExist:
			logger.warning(f"User not found for token: {token}")
			return None

	async def send_group_message(self, group_name, message):
		# Utilisation de self.room_group_name pour s'assurer que la bonne room est utilisée
		group_name = self.room_group_name  # Utilisation explicite de self.room_group_name

		if group_name in self.groups:
			logger.debug(f"Sending message to group {group_name}: {message}")
			for channel_name in self.groups[group_name]:
				try:
					await self.channel_layer.send(channel_name, {
						'type': 'chat_message',
						'message': message['message'],
						'username': message['username'],
						'room': message['room']
					})
					logger.debug(f"Message sent to {channel_name} in room {message['room']}: {message}")
				except Exception as e:
					logger.error(f"Failed to send message to {channel_name} in room {group_name}: {str(e)}")
		else:
			logger.error(f"Group {group_name} does not exist, unable to send message")

	async def chat_message(self, event):
		message = event['message']
		username = event.get('username', 'Anonyme')
		room = event.get('room', 'unknown')

		# Log pour vérifier le username avant envoi
		logger.info(f"Sending chat message from username: {username} in room: {room}")

		# Envoyer le message au WebSocket
		await self.send(text_data=json.dumps({
			'type': 'chat_message',
			'message': f'{username}: {message}',
			'room': room
		}))
