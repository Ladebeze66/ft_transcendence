# /pong/game/tournament.py

import json
from django.template.loader import render_to_string

class TournamentMatchMaker:
    def __init__(self):
        self.waiting_players = []

    async def add_player(self, player):
        if player not in self.waiting_players:
            self.waiting_players.append(player)
            print(f"User {player.user.username} joins the TOURNAMENT WAITING ROOM")
            await self.update_waiting_room()

    async def remove_player(self, player):
        if player in self.waiting_players:
            self.waiting_players.remove(player)
            await self.update_waiting_room()

    async def update_waiting_room(self):
        html = self.generate_waiting_room_html()
        for player in self.waiting_players:
            await player.send(json.dumps({
                'type': 'update_waiting_room',
                'html': html
            }))

    def generate_waiting_room_html(self):
        context = {
            'players': [player.user.username for player in self.waiting_players]
        }
        return render_to_string('pong/tournament_waiting_room.html', context)

# Instance of the class
tournament_match_maker = TournamentMatchMaker()