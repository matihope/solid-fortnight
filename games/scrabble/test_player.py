from modules.game_server.connection_helper import gen_cmd
import pygame
from modules import basic_classes
from modules import basic_globals


class Player(basic_classes.UpdatableObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sprite1 = pygame.Surface((self.size, self.size))
        sprite1.fill(basic_globals.GREEN)
        self.sprites = [sprite1]

    def update(self, keys, mouse, delta_time):
        super().update_physics(keys, mouse, delta_time)

        delta_x = keys[pygame.K_d] - keys[pygame.K_a]
        delta_y = keys[pygame.K_s] - keys[pygame.K_w]
        self.x += delta_x * 5
        self.y += delta_y * 5

        # if delta_x != 0 or delta_y != 0:
        #     if self.parent.client_id > 0:
        #         self.parent.connection.send_message(
        #             gen_cmd(
        #                 'SETPOS', [self.x, self.y]
        #             )
        #         )


class JoinedPlayer(basic_classes.DrawableObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = kwargs.get('id')
        sprite1 = pygame.Surface((self.size, self.size))
        sprite1.fill(basic_globals.RED)
        self.sprites = [sprite1]
