from .points import ScoreCalculator

class GameHandler:

    def __init__(self, game_js, deuces_allowed):
        self.points = game_js['points']
        self.deuces_allowed = deuces_allowed
        self.us_serving = game_js['server'] == "you"

    def get_game_scores(self):
        sc = ScoreCalculator(self.deuces_allowed)
        game_scores = []
        for point in self.points:
            sc.add_point(
                us_winner=point['winner'] == "you",
                us_server=point['server'] == "you"
            )
            game_scores.append(sc.score_dict.copy())
        return game_scores, sc.game_winner