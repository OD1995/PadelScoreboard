from dataclasses import dataclass
from .set import SetDto
from datetime import datetime

@dataclass
class MatchDto:
    start_timestamp: datetime
    sets: list[SetDto]