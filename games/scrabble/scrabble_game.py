from modules import \
    basic_classes, \
    basic_globals, \
    game_class


class ScrabbleGame(game_class.Game):
    def __init__(self, width, height, fps=60):
        super().__init__(width, height, fps)
        self.bg_color = (50, 50, 50)

    def update(self, delta_time):
        super().update(delta_time)
