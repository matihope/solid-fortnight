from games.scrabble.test_player import JoinedPlayer, Player
from modules import \
    basic_classes, \
    basic_globals, \
    game_class
from modules.game_server.connection_helper import gen_cmd
from modules.game_server.network import NetworkEvents
import pygame

class ScrabbleGame(game_class.Game):
    def __init__(self, width, height, fps=60):
        super().__init__(width, height, fps)
        self.bg_color = (50, 50, 50)

        self.main_player = Player(x=50, y=30, size=30)
        self.add_updatable(self.main_player)

    def update(self, delta_time):
        super().update(delta_time)

    def process_event(self, e):
        if e.type == NetworkEvents.EVENT_INIT:
            print(f'Initialized with id {e.client_id}')
            self.client_id = e.client_id
            self.connection.send_message(gen_cmd('PLAYERJOIN', [self.main_player.x,
                                                                self.main_player.y]))

        elif e.type == NetworkEvents.EVENT_DISCONNECT:
            print(f'{e.client_id} has left the game.')
            player_to_delete = self.other_connections.pop(e.client_id)
            self.remove_obj(player_to_delete)

        elif e.type == NetworkEvents.EVENT_ACTION:
            if e.action == 'SETPOS':
                player_id, x, y = [int(a) for a in e.args]
                self.other_connections[player_id].x = x
                self.other_connections[player_id].y = y

            elif e.action == 'PLAYERJOIN':
                player_id, x, y = [int(a) for a in e.args]
                # Tell new player about current player
                self.connection.send_message(
                    gen_cmd('TOCLIENT', [player_id, 'PLAYERJOINEDBEFORE',
                                         self.main_player.x, self.main_player.y])
                )
                self.other_connections[player_id] = JoinedPlayer(client_id=player_id, size=30, x=x, y=y)
                self.add_drawable(self.other_connections[player_id])

            elif e.action == 'PLAYERJOINEDBEFORE':
                player_id, x, y = [int(a) for a in e.args]
                self.other_connections[player_id] = JoinedPlayer(client_id=player_id, size=30, x=x, y=y)
                self.add_drawable(self.other_connections[player_id])

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                self.connection.send_message(gen_cmd('SAY', ['HELLO WORLD!']))
            for pl in self.other_connections.keys():
                self.connection.send_message(gen_cmd('PING', [pl]))
