# /pong/game/tournament.py
import json
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

class TournamentMatchMaker:
    def __init__(self):
        self.waiting_players = []
        logger.debug("TournamentMatchMaker initialized with an empty waiting_players list")

    async def add_player(self, player):
        if player not in self.waiting_players:
            self.waiting_players.append(player)
            logger.info(f"User {player.user.username} added to the TOURNAMENT WAITING ROOM")
            await self.update_waiting_room()
        else:
            logger.warning(f"User {player.user.username} is already in the TOURNAMENT WAITING ROOM")

    async def remove_player(self, player):
        if player in self.waiting_players:
            self.waiting_players.remove(player)
            logger.info(f"User {player.user.username} removed from the TOURNAMENT WAITING ROOM")
            await self.update_waiting_room()
        else:
            logger.warning(f"Attempt to remove non-existent user {player.user.username} from the TOURNAMENT WAITING ROOM")

    async def update_waiting_room(self):
        logger.debug("Updating TOURNAMENT WAITING ROOM")
        html = self.generate_waiting_room_html()
        for player in self.waiting_players:
            await player.send(json.dumps({
                'type': 'update_waiting_room',
                'html': html
            }))
        logger.info("TOURNAMENT WAITING ROOM updated and sent to all players")

    def generate_waiting_room_html(self):
        logger.debug("Generating TOURNAMENT WAITING ROOM HTML")
        context = {
            'players': [player.user.username for player in self.waiting_players]
        }
        html = render_to_string('pong/tournament_waiting_room.html', context)
        logger.info("TOURNAMENT WAITING ROOM HTML generated successfully")
        return html

# Instance of the class
tournament_match_maker = TournamentMatchMaker()
