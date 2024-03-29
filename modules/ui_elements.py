
import pygame

pygame.font.init()

DEFAULT_FONT = pygame.font.SysFont('', 28)
DEFAULT_MINI_FONT = pygame.font.SysFont('', 14)
DEFAULT_MONOSPACE_FONT = pygame.font.SysFont('monospace', 22, True)
DEFAULT_FONT_COLOR = (255, 255, 255)


class Label:
    def __init__(self, x, y, text, width=0, height=0, **kwargs):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.font = kwargs.get('font', DEFAULT_FONT)
        self.font_color = kwargs.get('font_color', DEFAULT_FONT_COLOR)

        self.text_anchor_x = kwargs.get('text_anchor_x', 'center')
        self.text_anchor_y = kwargs.get('text_anchor_y', 'center')
        self.text_offset_x = kwargs.get('text_offset_x', 0)
        self.text_offset_y = kwargs.get('text_offset_y', 0)
        self._text = ''
        self.text_obj = None
        self.text_pos = ()
        self.text = text

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value) -> None:
        self._text = str(value)
        self.text_obj = self.font.render(self._text, True, self.font_color)
        self.text_pos = [self.x, self.y]
        self.text_pos[0] += self.text_offset_x
        self.text_pos[1] += self.text_offset_y
        # apply horizontal anchor
        if self.text_anchor_x == 'left':
            pass
        elif self.text_anchor_x == 'center':
            self.text_pos[0] += self.width // 2
            self.text_pos[0] -= self.text_obj.get_width() // 2
        elif self.text_anchor_x == 'right':
            self.text_pos[0] += self.width
            self.text_pos[0] -= self.text_obj.get_width()
        # apply vertical anchor
        if self.text_anchor_y == 'top':
            pass
        elif self.text_anchor_y == 'center':
            self.text_pos[1] += self.height // 2
            self.text_pos[1] -= self.text_obj.get_height() // 2
        elif self.text_anchor_y == 'bottom':
            self.text_pos[1] += self.height
            self.text_pos[1] -= self.text_obj.get_height()


class Button(Label):
    def __init__(self, x, y, width, height, text, action=None,
                 colors=((160, 26, 88), (114, 60, 112), (69, 94, 137)),
                 anchor_x='center', anchor_y='center', **kwargs):

        if anchor_x == 'left':
            pass
        elif anchor_x == 'center':
            x -= width // 2
        elif anchor_x == 'right':
            x -= width

        if anchor_y == 'top':
            pass
        elif anchor_y == 'center':
            y -= height // 2
        elif anchor_y == 'bottom':
            y -= height

        super().__init__(x, y, text, width, height, **kwargs)
        self.colors = colors
        self.color = self.colors[0]
        self.action = action
        self.pressed_before = False
        self.pressed_before_buttons: tuple[bool, bool, bool]
        self.long_press = kwargs.get('long_press', False)
        self.tick_time = kwargs.get('tick_time', 0.1) * 1000
        self.tick_current = 0.0

    def check_collision(self, point: tuple[float, float]) -> bool:
        if point[0] < self.x:
            return False
        if point[1] < self.y:
            return False
        if point[0] > self.x + self.width:
            return False
        if point[1] > self.y + self.height:
            return False
        return True

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.color, (self.x, self.y, self.width, self.height)
        )
        surface.blit(self.text_obj, self.text_pos)

    def update(self, keys, mouse, dt, events):
        self.color = self.colors[0]
        if self.check_collision(mouse.get_pos()):
            self.color = self.colors[1]
            pressed = mouse.get_pressed()

            if any(pressed):
                self.color = self.colors[2]

                if self.long_press:
                    if not self.pressed_before:
                        self.action(self, pressed)
                    if self.tick_current >= self.tick_time:
                        self.tick_current %= self.tick_time
                        self.action(self, pressed)
                    self.tick_current += dt
            else:
                if not self.long_press:
                    if self.pressed_before:
                        self.action(self, self.pressed_before_buttons)

                self.tick_current = 0

            self.pressed_before = any(pressed)
            self.pressed_before_buttons = pressed
