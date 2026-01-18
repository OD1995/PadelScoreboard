from ..dtos import PointDto

class ScoreCalculator:

    def __init__(self, deuces_allowed, first_point:PointDto):
        self.us = "us"
        self.them = "them"
        self.score_dict = {
            self.us : "0",
            self.them : "0",
            "server" : self.get_server(first_point)
        }
        self.deuces_allowed = deuces_allowed
        self.deuce_count = 0
        # self.game_over = False
        self.game_winner = None
        self.is_deuce = True

        self.GAME_NOT_STARTED_YET = "-"
        self.OPPONENT_ON_ADVANTAGE = "/"
        self.ADVANTAGE = "AD"

    def get_server(self, point:PointDto):
        us_server = point.serving_pair == "us"
        return self.us if us_server else self.them

    def add_point(self, point:PointDto):
        us_winner = point.winner == "us"        
        self.score_dict['server'] = self.get_server(point)
        winner = self.us if us_winner else self.them
        loser = self.them if us_winner else self.us
        match self.score_dict[winner]:
            case "0":
                self.score_dict[winner] = "15"
            case "15":
                self.score_dict[winner] = "30"
            case "30":
                self.score_dict[winner] = "40"
            case "40":
                if self.score_dict[loser] == "40":
                    if self.deuces_allowed > self.deuce_count:
                        self.score_dict[winner] = self.ADVANTAGE
                        self.score_dict[loser] = self.OPPONENT_ON_ADVANTAGE
                    else:
                        self.set_game_over(winner)
                else:
                    self.set_game_over(winner)
            case self.OPPONENT_ON_ADVANTAGE:
                self.score_dict[winner] = "40"
                self.score_dict[loser] = "40"
            case self.ADVANTAGE:
                self.set_game_over(winner)
        self.update_deuce_count()

    def update_deuce_count(self):
        us_40 = self.score_dict[self.us] == "40"
        tied = self.score_dict[self.us] == self.score_dict[self.them]
        if us_40 and tied:
            self.deuce_count += 1

    def set_game_over(self, point_winner):
        # self.game_over = True
        self.game_winner = point_winner
        self.score_dict[self.us] = self.GAME_NOT_STARTED_YET
        self.score_dict[self.them] = self.GAME_NOT_STARTED_YET