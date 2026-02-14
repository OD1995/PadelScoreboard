from .points import ScoreCalculator, TiebreakGameScoreCalculator, NormalGameScoreCalculator
from ..dtos import GameDto
from datetime import datetime
from copy import deepcopy

class GameHandler:

    def __init__(
        self,
        game: GameDto,
        us_name: str,
        them_name: str,
        deuces_allowed: int,
        match_stats: dict
    ):
        self.game = game
        self.us_name = us_name
        self.them_name = them_name
        self.deuces_allowed = deuces_allowed
        self.match_stats = match_stats

    def get_game_scores(self, is_first_point_of_match, is_last_game_of_set):
        # print(f"{datetime.now()} - get_game_scores init")
        sc_initialiser = TiebreakGameScoreCalculator if self.game.is_tiebreak else NormalGameScoreCalculator
        sc = sc_initialiser(self.deuces_allowed, self.game.points[0], self.us_name, self.them_name, self.match_stats)
        game_scores = []
        match_stats_array = []
        if is_first_point_of_match:
            game_scores.append(sc.score_dict.copy())
            match_stats_array.append(deepcopy(sc.match_stats))
        for point_ix, point in enumerate(self.game.points):
            is_last_game_point = point_ix == len(self.game.points) - 1
            sc.add_point(
                point=point,
                is_last_game_point=is_last_game_point,
                is_last_set_point=is_last_game_point and is_last_game_of_set
            )
            game_scores.append(sc.score_dict.copy())
            match_stats_array.append(deepcopy(sc.match_stats))
        return game_scores, sc.game_winner, match_stats_array