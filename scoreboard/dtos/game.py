from dataclasses import dataclass
from .point import PointDto

@dataclass
class GameDto:
    points: list[PointDto]