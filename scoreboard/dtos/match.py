from dataclasses import dataclass
from .set import SetDto

@dataclass
class MatchDto:
    sets: list[SetDto]