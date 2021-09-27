from modules.game_server.connection_helper import gen_cmd
import modules.game_server.network as network
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
    conn.start()

    clock = pygame.time.Clock()
    while game.run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                game.run = False

            if e.type == network.NetworkEvents.EVENT_ACTION:
                if e.action == 'INIT':
                    print(f'INITIALIZED WITH ID {e.args[0]}')

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    network.send_message(conn, gen_cmd('SAY', ['HELLO WORLD!']))

        game.update(clock.tick(game.FPS))
        game.draw()
        win.blit(game.get_surface(), (0, 0))  # Real drawing
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
    exit(0)
