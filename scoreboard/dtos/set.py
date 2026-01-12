from dataclasses import dataclass
from .game import GameDto

@dataclass
class SetDto:
    games: list[GameDto]