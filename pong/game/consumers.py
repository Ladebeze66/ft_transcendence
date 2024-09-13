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

###################################################################CHAT###################################################################
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

		except Exception as e:
			logger.error(f"Erreur lors de la connexion WebSocket: {str(e)}")

	async def disconnect(self, close_code):
		try:
			# Retirer l'utilisateur du groupe en mémoire
			if self.room_group_name in self.groups:
				self.groups[self.room_group_name].remove(self.channel_name)
				if not self.groups[self.room_group_name]:
					del self.groups[self.room_group_name]

			await self.send_message(
				'chat_message',
				self.user.username if hasattr(self, "user") else "Unknown",
				f'{self.user.username if hasattr(self, "user") else "Unknown"} a quitté le chat',
				self.room_group_name
			)
			logger.info(f"{self.user.username if hasattr(self, 'user') else 'Unknown'} déconnecté du WebSocket de chat dans la room {self.room_group_name}")
		except Exception as e:
			logger.error(f"Erreur lors de la déconnexion WebSocket du chat: {str(e)}")

	async def receive(self, text_data):
		try:
			data = json.loads(text_data)
			message_type = data.get('type')
			username = data.get('username')

			# Log pour vérifier que le message est bien reçu
			logger.info(f"Message reçu: {data}")
			# Log pour vérifier que le username est bien reçu
			logger.info(f"Message reçu avec username: {username}")
			if not username:
				logger.error(f"Username missing in message: {data}")
				await self.send(text_data=json.dumps({'type': 'error', 'message': 'Username is missing'}))
				return

			# Gestion des types de messages
			if message_type == 'authenticate':
				logger.info(f"Authentification demandée pour {username}")
				await self.authenticate(data.get('token'), username)

			elif message_type == 'chat_message':
				if 'message' not in data:
					logger.error(f"Format de message incorrect : {data}")
					await self.send(text_data=json.dumps({'type': 'error', 'message': 'Format de message incorrect'}))
					return

				message = data['message']
				logger.info(f"Message envoyé par {username}: {message}")

				# Envoyer le message à tous les autres utilisateurs de la room
				await self.send_message('chat_message', username, message, self.room_group_name)

			# Gestion de la commande /b pour bloquer un utilisateur
			elif message_type == 'block_user':
				target_user = data.get('target_user')	
				if target_user == username:
					await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot block yourself'}))
				else:
					logger.info(f"{username} tente de bloquer {target_user}")
					await self.handle_block_user(data)

			# Gestion de la commande /i pour inviter un utilisateur
			elif message_type == 'invite_user':
				target_user = data.get('target_user')
				if target_user == username:
					await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot invite yourself'}))
				else:
					logger.info(f"{username} tente d'inviter {target_user}")
					await self.handle_invite_user(data)

			# Gestion de la réponse à l'invitation
			elif message_type == 'invite_response':
				response = data.get('response')
				inviter = data.get('inviter')
				await self.handle_invite_response(inviter, username, response, self.room_group_name)

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
		username = data['username']
		target_user = data['target_user']

		# Log les données reçues pour handle_block_user
		logger.info(f"handle_block_user appelé avec : {data}")

		# Validation de l'existence du joueur ciblé dans la room
		if target_user not in self.groups.get(self.room_group_name, []):
			logger.error(f"Target user {target_user} does not exist in room {self.room_group_name}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': f'Target user {target_user} not found in room'}))
			return

		# Validation pour éviter qu'un utilisateur ne se bloque lui-même
		if target_user == username:
			logger.warning(f"Block attempt failed: {username} tried to block themselves")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot block yourself'}))
			return

		# Logique de blocage réussie
		logger.info(f"Block request: {username} has blocked {target_user}")
	
		# Envoi d'un message de succès au client
		await self.send(text_data=json.dumps({
			'type': 'success',
			'user': username,
			'message': f'You have successfully blocked {target_user}',
			'target_user': target_user,
			'success': True
		}))

		# Envoi d'un message à la room pour notifier du blocage
		await self.send_message('block_user', username, f'{target_user} has been blocked by {username}', self.room_group_name)

	async def handle_invite_user(self, data):
		username = data['username']
		target_user = data['target_user']

		# Log les données reçues pour handle_invite_user
		logger.info(f"handle_invite_user appelé avec : {data}")

		room = data.get('room')

		# Validation de l'existence de la room
		if not room:
			logger.error(f"Room missing in invite request: {data}")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Room is missing in invite request'}))
			return

		# Validation pour éviter qu'un utilisateur ne s'invite lui-même
		if target_user == username:
			logger.warning(f"Invite attempt failed: {username} tried to invite themselves")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot invite yourself'}))
			return

		# Logique d'envoi d'une invitation réussie
		logger.info(f"{username} successfully invited {target_user} to a quick match in room {room}")

		# Envoi d'un message de succès au client
		await self.send(text_data=json.dumps({
			'type': 'success',
			'user': username,
			'message': f'Invitation sent to {target_user}',
			'target_user': target_user,
			'success': True
		}))

		# Envoi d'un message à la room pour notifier l'invitation
		await self.send_message('invite', username, f'{username} invited {target_user} to a quick match', room)

	async def handle_invite_response(self, inviter, username, response, room):
		# Log des informations reçues pour la réponse à l'invitation
		logger.info(f"handle_invite_response appelé avec : inviter={inviter}, username={username}, response={response}, room={room}")

		# Vérification de la réponse de l'utilisateur invité
		if response == 'yes':
			# Log de l'acceptation de l'invitation
			logger.info(f"{username} a accepté l'invitation de {inviter} pour la room {room}")
			# Envoi du message de réponse positive à la room
			await self.send_message('invite_response', username, f'{username} has accepted the invitation from {inviter}', room)
		else:
			# Log du refus de l'invitation
			logger.info(f"{username} a refusé l'invitation de {inviter} pour la room {room}")
			# Envoi du message de réponse négative à la room
			await self.send_message('invite_response', username, f'{username} has declined the invitation from {inviter}', room)

	async def authenticate(self, token, username):
		if not token:
			logger.error("Token is None, authentication cannot proceed")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'Token is missing'}))
			return
	
		# Log du token et du username pour vérification
		logger.info(f"Authentication attempt with token: {token} and username: {username}")
	
		try:
			user = await self.get_user_from_token(token)
			if user:
				self.user = user
				logger.info(f"User {username} authenticated successfully")
		
				# Envoyer un message d'authentification réussie au client
				await self.send(text_data=json.dumps({'type': 'authenticated', 'username': username}))

				# Envoyer le message de bienvenue après l'authentification réussie
				await self.send_message('chat_message', username, f' a rejoint le chat {self.room_group_name}', self.room_group_name)
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
		if group_name in self.groups:
			logger.debug(f"Sending message to group {group_name}: {message}")
			for channel_name in self.groups[group_name]:
				await self.channel_layer.send(channel_name, {
					'type': message['type'],
					'message': message['message'],
					'username': message['username'],
					'room': message['room']
				})
				logger.debug(f"Message sent to {channel_name} in room {message['room']}: {message}")

	async def send_message(self, message_type, username, message, room):
		"""Envoie un message à la room avec le username"""
		await self.send_group_message(
			room,
			{
				'type': message_type,
				'username': username,
				'message': message,
				'room': room
			}
		)
		logger.info(f"Message envoyé avec username: {username} - {message}")
 
	async def chat_message(self, event):
		message = event['message']
		username = event.get('username', 'Anonyme')
		room = event.get('room', 'unknown')

		# Log pour vérifier le username avant envoi
		logger.info(f"Sending chat message from username: {username} in room: {room}")

		# Envoyer le message au WebSocket
		await self.send(text_data=json.dumps({
			'type': 'chat_message',
			'username': username,
			'message': f'{message}',
			'room': room
		}))
