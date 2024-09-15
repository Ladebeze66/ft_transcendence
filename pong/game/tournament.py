# /pong/game/tournament.py

import json
import asyncio
from django.template.loader import render_to_string
import random
from .matchmaking import match_maker
from .game import Game
from .models import Tournoi
from .utils import create_tournament, update_tournament, getlen
from asgiref.sync import sync_to_async


TOURNAMENT_NAMES = [
    "Champions Clash", "Ultimate Showdown", "Battle Royale", 
    "Victory Cup", "Legends Tournament", "Elite Series", "Clash of 42",
    "Shibuya incident", "Cunning Game", "Elite of the Stars"
]

TOURNAMENT_NAMES =  [
    "Champion's Clash", "Ultimate Showdown", "Battle Royale",
    "Victory's Cup", "Legends Tournament", "Elite Series", "Clash of 42",
    "Shibuya Incident", "Cunning Game", "Elite of the Stars", "Chaku's Disciples"
]

class TournamentMatch(Game):
    def __init__(self, game_id, player1, player2, tournament):
        # Initialize the parent Game class with the provided parameters
        super().__init__(game_id, player1, player2, False)        
        # Store the current game instance in active games
        match_maker.active_games[game_id] = self        
        # Store the tournament instance
        self.tournament = tournament

    async def end_game(self, disconnected_player=None):
        # Call the parent class's end_game method
        await super().end_game(disconnected_player)
        # Handle the end of the match in the tournament context
        await self.tournament.handle_match_end(self)
        if self.game_id in match_maker.active_games:
            del match_maker.active_games[self.game_id]

class TournamentMatchMaker:
    def __init__(self):
        self.waiting_players = []
        self.matches = []
        self.rounds = []
        self.current_round = 0
        self.games = 0
        self.tournament_state = "waiting" #Can be "waiting", "in_progress", or "ended"
        self.name = random.choice(TOURNAMENT_NAMES)
        self.final_name = ""
        self.tournoi_reg = None

    async def add_player(self, player):
        if self.tournament_state == "waiting" and player not in self.waiting_players:
            self.waiting_players.append(player)
            if player:
                print(f"User {player.user.username} joins the TOURNAMENT WAITING ROOM")
            else:
                print("BOT joins the TOURNAMENT WAITING ROOM")
            await self.update_waiting_room()

    async def update_waiting_room(self):
        html = self.generate_waiting_room_html()
        for player in self.waiting_players:
            await self.send_to_player(player, {
                'type': 'update_tournament_waiting_room',
                'html': html
            })

    def generate_waiting_room_html(self):
        context = {
            'players': [player.user.username if player else 'BYE' for player in self.waiting_players],
            'tournament_state': self.tournament_state,
            'players_count': len(self.waiting_players),
            'min_players_to_start': 3  # You can adjust this number as needed
        }
        return render_to_string('pong/tournament_waiting_room.html', context)

    async def send_to_player(self, player, data):
        if player:
            await player.send(json.dumps(data))

    async def remove_player(self, player):
        if player in self.waiting_players:
            self.waiting_players.remove(player)
            await self.update_waiting_room()

    # Tournament start method
    async def start_tournament(self):

        if len(self.waiting_players) < 2:
            return False
        if len(self.waiting_players) % 2 == 0:
            await self.add_player(None)
        self.tournament_state = "in_progress"
        random.shuffle(self.waiting_players)
        self.current_round = 0
        len_tournament = await sync_to_async(getlen)()
        self.final_name = self.name + " #" + str(len_tournament + 1)
        self.tournoi_reg = await sync_to_async(create_tournament)(self.final_name, len(self.waiting_players))
        await self.advance_tournament()
        return True

    async def advance_tournament(self):
        players = self.waiting_players        
        while len(players) > 1:
            self.current_round += 1
            print(f"Starting round {self.current_round} with {len(players)} players")            
            await self.create_matches(players)
            await self.update_brackets()
            await self.start_round_matches()            
            # Wait for all matches in the current round to finish
            current_round_matches = self.rounds[-1]
            while not all(match.ended for match in current_round_matches):
                await asyncio.sleep(1)  # Wait for 1 second before checking again            
            # Get winners for the next round
            players = self.get_round_winners()
            print(f"Round {self.current_round} finished. {len(players)} players advancing.")        
        # Tournament has ended
        await self.update_brackets()
        await self.end_tournament(players[0] if players else None)

    async def create_matches(self, players):
        matches = []
        for i in range(0, len(players), 2):
            self.games += 1
            if i + 1 < len(players):
                # Create a new instance of TournamentMatch for this round
                match = TournamentMatch(self.games, players[i], players[i + 1], self)
                matches.append(match)
            else:
                # Create a BYE match where the second player is None
                match = TournamentMatch(self.games, players[i], None, self) # BYE match
                matches.append(match)
            
            # Assign the new match instance to the players
            if players[i]:
                await players[i].set_game(match)
            if i + 1 < len(players):
                if players[i + 1]:
                    await players[i + 1].set_game(match)

        self.rounds.append(matches)
        self.matches.extend(matches)

    async def update_brackets(self):
        html = self.generate_bracket_html()
        for player in self.waiting_players:
            await self.send_to_player(player, {
                'type': 'update_brackets',
                'html': html
            })

    def generate_bracket_html(self):
        context = {
            'tournament_rounds': self.get_tournament_data()
        }
        return render_to_string('pong/tournament_brackets.html', context)

    def get_tournament_data(self):
        return [
            [
                {
                    'player1': match.player1.user.username if match.player1 else 'BYE',
                    'player2': match.player2.user.username if match.player2 else 'BYE',
                    'winner': match.game_state['player1_name'] if match.game_state['player1_score'] > match.game_state['player2_score'] else match.game_state['player2_name'] if match.ended else None,
                    'score1': match.game_state['player1_score'],
                    'score2': match.game_state['player2_score']
                }
                for match in round_matches
            ]
            for round_matches in self.rounds
        ]

    async def start_round_matches(self):
        print(f"Starting TOURNAMENT round #{self.current_round}")
        for match in self.rounds[-1]:
            if match.player1 and match.player2:
                await match_maker.notify_players(match.player1, match.player2, match.game_id, False)
                asyncio.create_task(match.start_game())
            elif match.player1:
                # Handle BYE match
                await match_maker.notify_players(match.player1, match.player2, match.game_id, False)
                #asyncio.create_task(match.start_game())
                match.game_state['player1_score'] = 3
                match.game_state['player2_score'] = 0
                await match.end_game()

    def get_round_winners(self):
        winners = []
        for match in self.rounds[-1]:
            if match.ended:
                winner = match.player1 if match.game_state['player1_score'] > match.game_state['player2_score'] else match.player2
                #if winner:
                winners.append(winner)
        return winners

    async def end_tournament(self, winner):
        self.tournament_state = "ended"
        winner_username = winner.user.username if winner else "No winner"
        print(f"The TOURNAMENT winner is {winner_username}")
        for player in self.waiting_players:
            await self.send_to_player(player, {
                'type': 'tournament_end',
                'winner': winner_username
            })
        
        await sync_to_async(update_tournament)(self.final_name, winner_username)
        # Reset tournament state
        self.waiting_players = []
        self.matches = []
        self.rounds = []
        self.current_round = 0
        self.games = 0

    async def handle_match_end(self, match):
        await self.update_brackets()

# Instance of the class
tournament_match_maker = TournamentMatchMaker()