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
    lobby = scrabble_game.Lobby(
        width=GLB['WINDOW_WIDTH'],
        height=GLB['WINDOW_HEIGHT'],
        fps=GLB['FPS']
    )
    conn = network.SocketConnection("192.168.1.28", 8888)
    conn.start()
    connected_players = {}
    game.connection = conn
    game.connected_players = connected_players

    clock = pygame.time.Clock()
    while game.run:
        for e in pygame.event.get():
            game.process_event(e)
            if e.type == pygame.QUIT:
                game.run = False
                conn.stop()

        game.update(clock.tick(game.FPS))
        game.draw()
        win.blit(game.get_surface(), (0, 0))  # Real drawing
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
