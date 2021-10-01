from modules.game_server.connection_helper import gen_cmd
import modules.game_server.network as network
from games.scrabble.test_player import JoinedPlayer, Player
import pygame
import json

from pygame import constants
from games.scrabble import scrabble_game

with open('game_settings.json') as f:
    GLB = json.load(f)

win = pygame.display.set_mode(
    (GLB['WINDOW_WIDTH'], GLB['WINDOW_HEIGHT']),
    flags=pygame.DOUBLEBUF | pygame.SCALED,
    vsync=True
)
pygame.display.set_caption('Scrabble!')


def main():
    game = scrabble_game.ScrabbleGame(
        width=GLB['WINDOW_WIDTH'],
        height=GLB['WINDOW_HEIGHT'],
        fps=GLB['FPS']
    )
    conn = network.SocketConnection("192.168.0.17", 8888)
    game.connection = conn
    conn.start()

    while not conn.connected:
        if conn.done:
            quit()

    p = Player(x=50, y=30, size=30)
    game.add_updatable(p)

    players = {}

    clock = pygame.time.Clock()
    while game.run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                game.run = False
                conn.send_message(gen_cmd('DISCONNECT', []))
                conn.stop()

            if e.type == network.NetworkEvents.EVENT_ACTION:
                # print(e.action, e.args)
                if e.action == 'INIT':
                    new_id = int(e.args.pop(0))
                    print(f'INITIALIZED WITH ID {new_id}')
                    game.client_id = new_id
                    conn.send_message(gen_cmd('PLAYERJOIN', [p.x, p.y]))

                elif e.action == 'PLAYERJOIN':
                    player_id, x, y = [int(a) for a in e.args]
                    # Tell new player about current player
                    conn.send_message(gen_cmd('TOCLIENT', [player_id, 'PLAYERJOINEDBEFORE', p.x, p.y]))
                    players[player_id] = JoinedPlayer(id=player_id, size=30, x=x, y=y)
                    game.add_drawable(players[player_id])

                elif e.action == 'PLAYERJOINEDBEFORE':
                    player_id, x, y = [int(a) for a in e.args]
                    players[player_id] = JoinedPlayer(id=player_id, size=30, x=x, y=y)
                    game.add_drawable(players[player_id])

                elif e.action == 'SETPOS':
                    player_id, x, y = [int(a) for a in e.args]
                    players[player_id].x = x
                    players[player_id].y = y

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    conn.send_message(gen_cmd('SAY', ['HELLO WORLD!']))

        game.update(clock.tick(game.FPS))
        game.draw()
        win.blit(game.get_surface(), (0, 0))  # Real drawing
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
