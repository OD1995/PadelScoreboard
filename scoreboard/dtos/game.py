from dataclasses import dataclass
from .point import PointDto

@dataclass
class GameDto:
    points: list[PointDto]
    is_tiebreak: bool

    def has_points(self):
        return len(self.points) > 0