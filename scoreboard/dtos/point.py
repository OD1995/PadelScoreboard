from dataclasses import dataclass
from datetime import datetime
from typing import Literal

@dataclass
class PointDto:
    winner: Literal["us", "them"]
    serving_pair: Literal["us", "them"]
    timestamp: datetime