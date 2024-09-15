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
	async def connect(self):
		
		try:
			# Récupérer le nom de la room à partir de l'URL
			self.room_group_name = self.scope['url_route']['kwargs']['room_name']
		
			# Accepter la connexion WebSocket
			await self.accept()
			# Ajouter l'utilisateur au groupe (room)
			await self.channel_layer.group_add(
				self.room_group_name,
				self.channel_name
			)

			self.username = self.scope['user'].username  # Assurez-vous d'avoir un utilisateur lié à la connexion
			logger.info(f"Connexion de l'utilisateur {self.username} à la room {self.room_group_name}")
			# Ajouter l'utilisateur à son propre groupe personnel (pour messages directs)
					
			
		except Exception as e:
			logger.error(f"Erreur lors de la connexion WebSocket: {str(e)}")

	async def disconnect(self, close_code):
		try:
			# Retirer l'utilisateur du groupe (room)
			await self.channel_layer.group_discard(
				self.room_group_name,
				self.channel_name
			)

			# Retirer l'utilisateur de son groupe personnel
			await self.channel_layer.group_discard(
				f"user_{self.username}",
				self.channel_name
			)

			# Envoyer un message indiquant que l'utilisateur a quitté la room
			await self.chat_message(
				'chat_message',
				self.user.username if hasattr(self, "user") else "Unknown",
				f'{self.user.username if hasattr(self, "user") else "Unknown"} a quitté le chat',
				self.room_group_name
			)
			logger.info(f"{self.user.username if hasattr(self, 'user') else 'Unknown'} déconnecté de la room {self.room_group_name}")

		except Exception as e:
			logger.error(f"Erreur lors de la déconnexion WebSocket: {str(e)}")

	async def receive(self, text_data):
		try:
			# Convertir les données JSON reçues en dictionnaire Python
			data = json.loads(text_data)
			message_type = data.get('type')
			username = data.get('username')
			message = data.get('message', None)
			target_user = data.get('target_user', None)

			logger.info(f"Message reçu: {data}")

			if not username:
				logger.error(f"Username manquant dans le message: {data}")
				await self.chat_message('error', 'server', 'Username is missing', self.room_group_name)
				return

			# Gestion des différents types de messages
			if message_type == 'authenticate':
				logger.info(f"Authentification demandée pour {username}")
				await self.authenticate(data.get('token'), username)
				return

			elif message_type == 'chat_message':
				logger.info(f"Message de chat envoyé par {username}: {message}")
				await self.chat_message('chat_message', username, message, self.room_group_name)

			elif message_type == 'block_user':
				logger.info(f"{username} tente de bloquer {target_user}")
				await self.handle_block_user(data)

			elif message_type == 'invite':
				await self.handle_invite_user(data)

			elif message_type == 'invite_response':
				await self.handle_invite_response(data)

			else:
				logger.warning(f"Type de message non géré: {message_type}")
				await self.chat_message('error', 'server', f"Unhandled message type: {message_type}", self.room_group_name)

		except json.JSONDecodeError as e:
			logger.error(f"Erreur de décodage JSON : {str(e)} - Données reçues : {text_data}")
			await self.chat_message('error', 'server', 'Invalid JSON format', self.room_group_name)

		except Exception as e:
			logger.error(f"Erreur lors de la réception du message: {str(e)}")
			await self.chat_message('error', 'server', 'Internal server error', self.room_group_name)

	async def chat_message(self, message_type, username, message, room):
		"""
		Fonction générale pour envoyer tout type de message via WebSocket à tous les utilisateurs dans la room.
		"""
		logger.info(f"Envoi d'un message de type {message_type} de {username} dans la room {room}")
		
		# Utilisation de channel_layer pour envoyer le message à tout le groupe (room)
		await self.channel_layer.group_send(
			room,
			{
				'type': 'send_group_message',  # Nom de la méthode qui va gérer ce message
				'username': username,
				'message': message,
				'room': room
			}
		)

	async def send_group_message(self, event):
		"""
		Cette fonction est appelée par channel_layer pour envoyer des messages à tous les utilisateurs dans une room.
		"""
		message = event['message']
		username = event.get('username', 'Anonyme')
		room = event.get('room', 'unknown')

		logger.info(f"Diffusion d'un message de {username} à la room {room}: {message}")

		# Envoi du message à chaque utilisateur dans la room via WebSocket
		await self.send(text_data=json.dumps({
			'type': 'chat_message',  # Le type de message qui sera renvoyé au client
			'username': username,
			'message': message,
			'room': room
		}))

	async def handle_block_user(self, data):
		username = data['username']
		target_user = data['target_user']

		logger.info(f"handle_block_user appelé avec : {data}")

		if target_user == username:
			logger.warning(f"{username} a tenté de se bloquer lui-même.")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot block yourself'}))
			return

		logger.info(f"{username} a bloqué {target_user}")
	
		# Utilisation correcte de l' f-string pour inclure la valeur de target_user
		await self.send(text_data=json.dumps({
			'type': 'block_user',
			'message': f'Vous avez bloqué les messages de {target_user}'
		}))

	async def handle_invite_user(self, data):
		# Récupération des informations de l'invitation
		inviter = data.get('username')
		target_user = data.get('target_user')
		room = data.get('room')

		# Validation des paramètres
		if not inviter:
			logger.error("Invitant manquant dans le message d'invitation")
			await self.chat_message('error', 'server', 'Invitant manquant', self.room_group_name)
			return

		if not target_user:
			logger.error("Utilisateur cible manquant dans le message d'invitation")
			await self.chat_message('error', 'server', 'Utilisateur cible manquant', self.room_group_name)
			return

		if not room:
			logger.error("Room manquante dans le message d'invitation")
			await self.chat_message('error', 'server', 'Room manquante', self.room_group_name)
			return

		logger.info(f"Invitation envoyée de {inviter} à {target_user} dans la room {room}")
		await self.chat_message('chat_message', 'server', f'{inviter} a invité {target_user} à rejoindre une partie {room}', room)

		# Envoi de l'invitation
		await self.channel_layer.group_send(
			room,
			{
				'type': 'invite',
				'inviter': inviter,
				'target_user': target_user,
				'room': room,
				'message': f'{inviter} vous a invité à rejoindre la room {room}.'
			}
		)

	async def handle_invite_response(self, data):
		inviter = data.get('inviter')
		username = data.get('username')  # L'utilisateur invité qui répond
		response = data.get('response')
		room = data.get('room')

		logger.info(f"{username} a répondu '{response}' à l'invitation de {inviter}")
		await self.chat_message('chat_message', 'server', f'{username} a répondu {response} à l\'invitation.', room)

		 # Si la réponse est 'yes', informer l'invitant que l'invité a accepté
		if response.lower() == 'yes':
			try:
				# Informer l'invitant que l'invitation a été acceptée
				await self.channel_layer.group_send(
					room,
					{
						'type': 'invite_response',
						'inviter': inviter,
						'username': username,
						'response': response,
						'room': room,
						'message': f'{username} a accepté l\'invitation.'
					}
				)
				 # Informer à la fois l'invité et l'invitant que le jeu va commencer
				await self.channel_layer.group_send(
					room,
					{
						'type': 'start_quick_match',
						'inviter': inviter,
						'username': username,
						'message': 'La partie va démarrer pour vous deux.',
					}
				)
			except Exception as e:
				logger.error(f"Error while sending invite response: {str(e)}")
				await self.chat_message('error', 'server', f'Internal server error: {str(e)}', room)
			
	# Méthode appelée pour envoyer l'invitation à l'utilisateur invité (target_user)
	async def invite(self, event):
		inviter = event['inviter']
		message = event['message']
		room = event['room']
		target_user = event['target_user']
		logger.info(f"invite: Envoi de l'invitation à l'utilisateur via WebSocket. Inviter={inviter}, Room={room}, Message={message}")

		# Envoyer le message d'invitation via WebSocket
		await self.send(text_data=json.dumps({
			'type': 'invite',
			'inviter': inviter,
			'target_user': target_user,
			'message': message,
			'room': room
		}))

	async def handle_invite_response(self, data):
		inviter = data.get('inviter')
		username = data.get('username')  # L'utilisateur invité qui répond
		response = data.get('response')
		room = data.get('room')

		logger.info(f"{username} a répondu '{response}' à l'invitation de {inviter}")
		await self.chat_message('chat_message', 'server', f'{username} a répondu {response} à l\'invitation.', room)

		# Envoi de la réponse directement à l'invitant dans la room
		await self.channel_layer.group_send(
			room,
			{
				'type': 'invite_response',  # Type de message 'invite_response'
				'inviter': inviter,
				'username': username,
				'room': room,
				'message': f'{username} a répondu {response} à l\'invitation.',
				'response': response  # Ajout de la réponse 'yes' ou 'no'
			}
		)

	async def invite_response(self, event):
		message = event['message']
		response = event.get('response')
		inviter = event.get('inviter')  # Récupérer l'inviteur		

		logger.info(f"invite_response: Envoi de la réponse à l'invitation via WebSocket. Message={message}, Response={response}, Inviter={inviter}")

		# Envoyer la réponse à l'invitation via WebSocket à l'invitant
		await self.send(text_data=json.dumps({
			'type': 'invite_response',
			'message': message,
			'response': response,
			'inviter': inviter
		}))

	async def authenticate(self, token, username):
		if not token:
			logger.error("Token est manquant, l'authentification ne peut pas se poursuivre.")
			await self.chat_message('error', 'server', 'Token is missing', self.room_group_name)
			return

		logger.info(f"Tentative d'authentification avec le token: {token} pour l'utilisateur: {username}")

		try:
			user = await self.get_user_from_token(token)
			if user:
				self.user = user
				logger.info(f"Utilisateur {username} authentifié avec succès")
				await self.chat_message('authenticated', username, 'Authentication successful', self.room_group_name)
				
				await self.channel_layer.group_add(
				f"user_{self.username}",  # Group name unique pour cet utilisateur
				self.channel_name
				)
				logger.info(f"Connexion de l'utilisateur {self.username} à son groupe personnel")
			else:
				logger.warning(f"Échec de l'authentification pour le token: {token}")
				await self.chat_message('error', username, 'Authentication failed', self.room_group_name)
		except Exception as e:
			logger.error(f"Erreur lors de l'authentification : {str(e)}")
			await self.chat_message('error', 'server', 'Internal server error', self.room_group_name)

	@sync_to_async
	def get_user_from_token(self, token):
		try:
			user = User.objects.filter(auth_token=token).first()
			logger.debug(f"Utilisateur trouvé : {user} pour le token : {token}")
			return user
		except User.DoesNotExist:
			logger.warning(f"Utilisateur non trouvé pour le token : {token}")
			return None 