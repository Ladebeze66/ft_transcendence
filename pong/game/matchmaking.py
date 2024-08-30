# /pong/game/matchmaking.py

import json
import asyncio
from .game import Game

class MatchMaker:
    def __init__(self):
        self.waiting_players = []
        self.active_games = {}
        self.matching_task = None
        self.timer = 0
        self.botgame = False

    async def add_player(self, player):
        if player not in self.waiting_players:
            self.waiting_players.append(player)
            print(f"User {player.user.username} joins the WAITING ROOM")
            if not self.matching_task or self.matching_task.done():
                self.matching_task = asyncio.create_task(self.match_loop())

    async def remove_player(self, player):
        if player in self.waiting_players:
            self.waiting_players.remove(player)
        
        for game in self.active_games.values():
            if player in [game.player1, game.player2]:
                await game.end_game(disconnected_player=player)
                del self.active_games[game.game_id]
                break

    async def match_loop(self):
        while True:
            if len(self.waiting_players) >= 2:
                player1 = self.waiting_players.pop(0)
                player2 = self.waiting_players.pop(0)
                print(f"*** MATCH FOUND: {player1.user.username} vs {player2.user.username}")
                await self.create_game(player1, player2, False)
            else:
                await asyncio.sleep(1)
                self.timer += 1
                # Waiting for more than 30s -> BOT game
                if self.timer >= 15 and self.waiting_players:
                    player1 = self.waiting_players.pop(0)
                    print(f"*** MATCH FOUND: {player1.user.username} vs BOT")
                    self.botgame = True
                    self.timer = 0
                    await self.create_bot_game(player1)
            if not self.waiting_players:
                break

    async def create_game(self, player1, player2, localgame):
        game_id = len(self.active_games) + 1
        if localgame:
            print(f"- Creating LOCAL game: #{game_id}")
        else:
            print(f"- Creating MATCH game: #{game_id}")
        new_game = Game(game_id, player1, player2, localgame)
        self.active_games[game_id] = new_game
        await player1.set_game(new_game)
        if not localgame:
            await player2.set_game(new_game)
        await self.notify_players(player1, player2, game_id, localgame)
        asyncio.create_task(new_game.start_game())

    async def create_bot_game(self, player1):
        game_id = len(self.active_games) + 1
        print(f"- Creating BOT game: #{game_id}")
        new_game = Game(game_id, player1, None, False)
        self.active_games[game_id] = new_game
        await player1.set_game(new_game)
        await self.notify_players(player1, None, game_id, False)
        asyncio.create_task(new_game.start_game())

    async def notify_players(self, player1, player2, game_id, localgame):
        if player2:
            await player1.send(json.dumps({
                'type': 'game_start',
                'game_id': game_id,
                'player1': player1.user.username,
                'player2': player2.user.username
            }))
            await player2.send(json.dumps({
                'type': 'game_start',
                'game_id': game_id,
                'player1': player1.user.username,
                'player2': player2.user.username
            }))
        else:
            if localgame:
                await player1.send(json.dumps({
                    'type': 'game_start',
                    'game_id': game_id,
                    'player1': player1.user.username,
                    'player2': player1.user2.username
                }))
            else:
                await player1.send(json.dumps({
                    'type': 'game_start',
                    'game_id': game_id,
                    'player1': player1.user.username,
                    'player2': 'BOT'
                }))

    async def handle_key_press(self, player, key):
        for game in self.active_games.values():
            if player in [game.player1, game.player2]:
                await game.handle_key_press(player, key)
                break

# Instance of the class
match_maker = MatchMaker()
