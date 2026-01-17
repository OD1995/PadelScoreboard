from dataclasses import dataclass
from .game import GameDto

@dataclass
class SetDto:
    games: list[GameDto]

    def has_points(self):
        for game in self.games:
            if game.has_points():
                return True
        return False