import pygame
import random
import math
from games.snake import snake_game

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('game1')


def main():
    game = snake_game.SnakeGame(width=WIDTH, height=HEIGHT, fps=60)

    clock = pygame.time.Clock()
    while game.run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                game.run = False

        game.update(clock.tick(game.FPS))
        game.draw()
        x = game.get_surface()
        # x = pygame.transform.scale(x, (WIDTH//2, HEIGHT//2))
        win.blit(x, (0, 0))  # Real drawing
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    print(pygame.display.Info())
    main()
    pygame.quit()
