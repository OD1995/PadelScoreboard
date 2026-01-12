from .points import ScoreCalculator
from ..dtos import GameDto

class GameHandler:

    def __init__(
        self,
        game:GameDto,
        deuces_allowed
    ):
        self.game = game
        self.deuces_allowed = deuces_allowed

    def get_game_scores(self):
        sc = ScoreCalculator(self.deuces_allowed)
        game_scores = []
        for point in self.game.points:
            sc.add_point(
                us_winner=point.winner == "us",
                us_server=point.serving_pair == "us"
            )
            game_scores.append(sc.score_dict.copy())
        return game_scores, sc.game_winner