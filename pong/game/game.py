# /pong/game/game.py

import json
import asyncio
import random
from datetime import datetime
from .utils import handle_game_data
from asgiref.sync import sync_to_async


class Game:
    def __init__(self, game_id, player1, player2, localgame):
        self.game_id = game_id
        self.player1 = player1
        self.player2 = player2
        self.localgame = localgame
        if self.localgame:
            self.botgame = False
            self.game_state = {
                'player1_name': player1.user.username,
                'player2_name': player1.user2.username,
                'player1_position': 150,
                'player2_position': 150,
                'ball_position': {'x': 390, 'y': 190},
                'ball_velocity': {'x': random.choice([-5, 5]), 'y': random.choice([-5, 5])},
                'player1_score': 0,
                'player2_score': 0,
                'game_text': ''
            }
        else:
            self.botgame = player2 is None
            self.game_state = {
                'player1_name': player1.user.username,
                'player2_name': player2.user.username if player2 else 'BOT',
                'player1_position': 150,
                'player2_position': 150,
                'ball_position': {'x': 390, 'y': 190},
                'ball_velocity': {'x': random.choice([-5, 5]), 'y': random.choice([-5, 5])},
                'player1_score': 0,
                'player2_score': 0,
                'game-text': ''
            }
        self.speed = 1
        self.game_loop_task = None
        self.ended = False
        self.p1_mov = 0
        self.p2_mov = 0
        self.bt1 = 0
        self.bt2 = 0
        self.start_time = None

    async def start_game(self):
        print(f"- Game #{self.game_id} STARTED")
        self.game_loop_task = asyncio.create_task(self.game_loop())
        self.start_time = datetime.now()
        print(f"  Begin MATCH at: {self.start_time}")

    async def game_loop(self):
        print("  In the game loop..")
        x = 0
        while not self.ended:
            if self.botgame:
                x += 1
                if x == 60:
                    await self.update_bot_position()
                    x = 0
            await self.handle_pad_movement()
            await self.update_game_state()
            await self.send_game_state()
            await asyncio.sleep(1/60)  # Around 60 FPS

    async def update_bot_position(self):
        future_ball_position = self.predict_ball_trajectory()

        target_y = future_ball_position['y']
        player2_position = self.game_state['player2_position']
        
        # Adjusts bot position based on expected ball position
        if player2_position < target_y < player2_position + 80:
            pass  #bot already placed
        elif player2_position < target_y:
            self.game_state['player2_position'] = min(player2_position + (50 * self.speed), 300)
        elif player2_position + 80 > target_y:
            self.game_state['player2_position'] = max(player2_position - (50 * self.speed), 0)

    def predict_ball_trajectory(self, steps=60):
    
        future_x = self.game_state['ball_position']['x']
        future_y = self.game_state['ball_position']['y']
        velocity_x = self.game_state['ball_velocity']['x']
        velocity_y = self.game_state['ball_velocity']['y']

        for _ in range(steps):
            future_x += velocity_x
            future_y += velocity_y

            # Dealing with bounces off walls
            if future_y <= 0 or future_y >= 300:
                velocity_y = -velocity_y  # Reverse the direction of vertical movement

        return {'x': future_x, 'y': future_y}

    async def update_game_state(self):
        if self.ended:
            return
        # Update ball position
        self.game_state['ball_position']['x'] += self.game_state['ball_velocity']['x']
        self.game_state['ball_position']['y'] += self.game_state['ball_velocity']['y']
        # Check for collisions with top and bottom walls
        if self.game_state['ball_position']['y'] <= 10 or self.game_state['ball_position']['y'] >= 390:
            self.game_state['ball_velocity']['y'] *= -1
        # Check for collisions with paddles
        if self.game_state['ball_position']['x'] <= 20 and \
            self.game_state['player1_position'] - 10 <= self.game_state['ball_position']['y'] <= self.game_state['player1_position'] + 90:
            if self.game_state['ball_velocity']['x'] < 0:
                self.game_state['ball_velocity']['x'] *= -1
                self.bt1 += 1
            self.update_ball_velocity()
        elif self.game_state['ball_position']['x'] >= 760 and \
            self.game_state['player2_position'] - 10 <= self.game_state['ball_position']['y'] <= self.game_state['player2_position'] + 90:
            if self.game_state['ball_velocity']['x'] > 0:
                self.game_state['ball_velocity']['x'] *= -1
                self.bt2 += 1
            self.update_ball_velocity()
        # Check if some player won the game
        if self.game_state['ball_position']['x'] <= 10:
            self.game_state['player2_score'] += 1
            if self.game_state['player2_score'] > 2:
                self.game_state['game_text'] = f"{self.game_state['player2_name']} WINS!"
                await self.send_game_state()
                await self.end_game()
            self.reset_ball()
        elif self.game_state['ball_position']['x'] >= 790:
            self.game_state['player1_score'] += 1
            if self.game_state['player1_score'] > 2:
                self.game_state['game_text'] = f"{self.game_state['player1_name']} WINS!"
                await self.send_game_state()
                await self.end_game()
            self.reset_ball()

    def reset_ball(self):
        self.game_state['ball_position'] = {'x': 390, 'y': 190}
        self.game_state['ball_velocity'] = {'x': random.choice([-5, 5]), 'y': random.choice([-5, 5])}
        self.speed = 1

    def update_ball_velocity(self):
        self.speed += 0.05
        if self.speed > 2:
            self.speed = 2
        self.game_state['ball_velocity']['x'] *= self.speed
        if self.game_state['ball_velocity']['x'] < -10:
            self.game_state['ball_velocity']['x'] = -10
        elif self.game_state['ball_velocity']['x'] > 10:
            self.game_state['ball_velocity']['x'] = 10
        self.game_state['ball_velocity']['y'] *= self.speed
        if self.game_state['ball_velocity']['y'] < -10:
            self.game_state['ball_velocity']['y'] = -10
        elif self.game_state['ball_velocity']['y'] > 10:
            self.game_state['ball_velocity']['y'] = 10

    async def send_game_state(self):
        if self.ended:
            return
        message = json.dumps({
            'type': 'game_state_update',
            'game_state': self.game_state
        })
        await self.player1.send(message)
        if not self.botgame:
            if not self.localgame:
                await self.player2.send(message)

    async def handle_key_press(self, player, key):
        if self.ended:
            return
        if self.localgame:
            if key == 'arrowup':
                self.p2_mov = -1
            elif key == 'arrowdown':
                self.p2_mov = 1
            elif key == 'w':
                self.p1_mov = -1
            elif key == 's':
                self.p1_mov = 1
        elif player == self.player1:
            if key == 'arrowup':
                self.p1_mov = -1
            elif key == 'arrowdown':
                self.p1_mov = 1
        elif player == self.player2:
            if key == 'arrowup':
                self.p2_mov = -1
            elif key == 'arrowdown':
                self.p2_mov = 1

    async def handle_pad_movement(self):
        if self.ended:
            return
        if self.p1_mov == -1:
            self.game_state['player1_position'] = max(self.game_state['player1_position'] - (5 * self.speed), 0)
        elif self.p1_mov == 1:
            self.game_state['player1_position'] = min(self.game_state['player1_position'] + (5 * self.speed), 300)
        if self.p2_mov == -1:
            self.game_state['player2_position'] = max(self.game_state['player2_position'] - (5 * self.speed), 0)
        elif self.p2_mov == 1:
            self.game_state['player2_position'] = min(self.game_state['player2_position'] + (5 * self.speed), 300)

    async def end_game(self, disconnected_player=None):
        if not self.ended:
            self.ended = True
            if self.game_loop_task:
                self.game_loop_task.cancel()            
            print(f"- Game #{self.game_id} ENDED")

            end_time = datetime.now()
            duration = (end_time -  self.start_time).total_seconds() / 60

            # Notify that one player left the game      
            if disconnected_player:
                remaining_player = self.player2 if disconnected_player == self.player1 else self.player1
                disconnected_name = disconnected_player.user.username
                message = json.dumps({
                    'type': 'player_disconnected',
                    'player': disconnected_name
                })
                if not self.botgame:
                    if not self.localgame:
                        await remaining_player.send(message)            
            # Notify both players that the game has ended
            end_message = json.dumps({
                'type': 'game_ended',
                'game_id': self.game_id
            })
            await self.player1.send(end_message)
            if not self.botgame:
                if not self.localgame:
                    await self.player2.send(end_message)
            await sync_to_async(handle_game_data)(self.game_state['player1_name'], self.game_state['player2_name'],
                           self.game_state['player1_score'], self.game_state['player2_score'],
                           self.bt1, self.bt2, duration, False, None)
