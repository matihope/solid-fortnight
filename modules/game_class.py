import pygame
from modules import basic_globals


class Game:
    def __init__(self, width, height, fps=60):
        self.draw_reg = []  # reg = registry
        self.update_reg = []

        self.WIDTH = width
        self.HEIGHT = height
        self.FPS = fps
        self.run = True

        self.bg_color = basic_globals.BLUE
        self.keys = None

        self.__surface = pygame.Surface((width, height))

    def update(self):
        """ Update self and objects """
        self.keys = pygame.key.get_pressed()
        for obj in self.update_reg:
            obj.update(self.keys)

    def draw(self):
        """ Draw objects to the surface """
        self.__surface.fill(self.bg_color)
        for obj in self.draw_reg:
            obj.draw(self.__surface)

    def add_updatable(self, obj):
        """ Add another updatable """
        self.update_reg.append(obj)
        self.add_drawable(obj)

    def add_drawable(self, obj):
        """ Add another drawable """
        self.draw_reg.append(obj)
        obj.add_parent(self)

    def get_surface(self):
        return self.__surface
