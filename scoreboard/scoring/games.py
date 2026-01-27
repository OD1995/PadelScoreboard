from .points import ScoreCalculator, TiebreakGameScoreCalculator, NormalGameScoreCalculator
from ..dtos import GameDto

class GameHandler:

    def __init__(
        self,
        game:GameDto,
        deuces_allowed
    ):
        self.game = game
        self.deuces_allowed = deuces_allowed

    def get_game_scores(self, is_first_point_of_match):
        sc_initialiser = TiebreakGameScoreCalculator if self.game.is_tiebreak else NormalGameScoreCalculator
        sc = sc_initialiser(self.deuces_allowed, self.game.points[0])
        game_scores = []
        if is_first_point_of_match:
            game_scores.append(sc.score_dict.copy())
        for point in self.game.points:
            sc.add_point(point)
            game_scores.append(sc.score_dict.copy())
        return game_scores, sc.game_winner