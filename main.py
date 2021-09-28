from modules.game_server.connection_helper import gen_cmd
import modules.game_server.network as network
from games.scrabble.test_player import JoinedPlayer, Player
import pygame
import json

from pygame import constants
from games.scrabble import scrabble_game

with open('game_settings.json') as f:
    GLB = json.load(f)


win = pygame.display.set_mode((GLB['WINDOW_WIDTH'], GLB['WINDOW_HEIGHT']))
pygame.display.set_caption('Scrabble!')


def main():
    game = scrabble_game.ScrabbleGame(width=GLB['WINDOW_WIDTH'], height=GLB['WINDOW_HEIGHT'], fps=GLB['FPS'])
    conn = network.SocketConnection("192.168.0.17", 8888)
    game.connection = conn
    conn.start()

    while not conn:
        pass

    p = Player(x=50, y=30, size=30)
    game.add_updatable(p)

    players = {}

    clock = pygame.time.Clock()
    while game.run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                game.run = False
                conn.stop()
                conn.send_message(gen_cmd('DISCONNECT', []))

            # so many events that other client cannot exit this loop XD
            if e.type == network.NetworkEvents.EVENT_ACTION:
                if e.action == 'INIT':
                    print(f'INITIALIZED WITH ID {e.args[0]}')
                    game.client_id = int(e.args[0])
                    conn.send_message(gen_cmd('PLAYERJOIN', [int(e.args[0]), 50, 30]))

                elif e.action == 'PLAYERJOIN':
                    player_id, x, y = [int(a) for a in e.args]
                    players[player_id] = JoinedPlayer(id=player_id, x=x, y=y, size=30)
                    game.add_drawable(players[player_id])

                elif e.action == 'SETPOS':
                    player_id, x, y = [int(a) for a in e.args]
                    players[player_id].x = x
                    players[player_id].y = y

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    conn.send_message(gen_cmd('SAY', ['HELLO WORLD!']))

        game.update(clock.tick(game.FPS))
        if game.client_id > 0:
            conn.send_message(gen_cmd('SETPOS', [game.client_id, p.x, p.y]))
        game.draw()
        win.blit(game.get_surface(), (0, 0))  # Real drawing
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
