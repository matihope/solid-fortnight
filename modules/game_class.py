import pygame
from modules import basic_globals


class Game:
    def __init__(self, width, height, fps=60, physics_fps=60):
        self.draw_regs = [[]]  # reg = registry
        self.update_regs = [[]]

        self.WIDTH = width
        self.HEIGHT = height
        self.FPS = fps
        self._physics_fps = None
        self.physics_update_threshold = None
        self.PHYSICS_FPS = physics_fps
        
        self.run = True

        self.delta_time = 1
        self.time_counter = 0

        self.bg_color = basic_globals.BLUE
        self.keys = None
        self.mouse = None

        self.connection = None
        self.client_id = -1

        self.__surface = pygame.Surface((width, height))

    @property
    def PHYSICS_FPS(self) -> int:
        return self._physics_fps

    @PHYSICS_FPS.setter
    def PHYSICS_FPS(self, value: int) -> None:
        self._physics_fps = value
        self.physics_update_threshold = 1000 / self.PHYSICS_FPS

    def update(self, delta_time):
        """ Update self and objects """
        self.delta_time = delta_time
        self.keys = pygame.key.get_pressed()
        self.mouse = pygame.mouse
        for lst in self.update_regs:
            for obj in lst:
                obj.update(self.keys, self.mouse, delta_time)

        self.time_counter += delta_time
        if self.time_counter > self.physics_update_threshold:
            self.time_counter -= self.physics_update_threshold
            for lst in self.update_regs:
                for obj in lst:
                    obj.update_physics(self.keys, self.mouse, delta_time)

    def draw(self):
        """ Draw objects to the surface """
        self.__surface.fill(self.bg_color)
        for lst in self.draw_regs:
            for obj in lst:
                obj.draw(self.__surface)

    def add_updatable(self, obj, update_order=0, draw_order=0):
        """ Add another updatable """
        if len(self.update_regs) > update_order:
            self.update_regs[update_order].append(obj)
        else:
            self.update_regs.append([obj])
        self.add_drawable(obj, draw_order=draw_order)

    def add_drawable(self, obj, draw_order=0):
        """ Add another drawable """
        if len(self.draw_regs) > draw_order:
            self.draw_regs[draw_order].append(obj)
        else:
            self.draw_regs.append([obj])
        obj.add_parent(self)

    def remove_obj(self, obj):
        """ Remove object from the registries """
        removed_from_draw = False
        removed_from_update = False
        for i in range(len(self.draw_regs)):
            if obj in self.draw_regs[i]:
                self.draw_regs[i].remove(obj)
                removed_from_draw = True
        for i in range(len(self.update_regs)):
            if obj in self.update_regs[i]:
                self.update_regs[i].remove(obj)
                removed_from_update = True
        return removed_from_draw, removed_from_update

    def get_surface(self):
        return self.__surface
