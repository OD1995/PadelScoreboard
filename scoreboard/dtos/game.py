from dataclasses import dataclass
from .point import PointDto

@dataclass
class GameDto:
    points: list[PointDto]

    def has_points(self):
        return len(self.points) > 0