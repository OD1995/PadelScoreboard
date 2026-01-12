class ScoreCalculator:

    def __init__(self, deuces_allowed):
        self.us = "us"
        self.them = "them"
        self.score_dict = {
            self.us : "0",
            self.them : "0",
        }
        self.deuces_allowed = deuces_allowed
        self.deuce_count = 0
        # self.game_over = False
        self.game_winner = None
        self.is_deuce = True

    def add_point(self, us_winner:bool, us_server:bool):
        self.score_dict['server'] = self.us if us_server else self.them
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
                        self.score_dict[winner] = "Ad"
                        self.score_dict[loser] = "X"
                    else:
                        self.set_game_over(winner)
                else:
                    self.set_game_over(winner)
            case "X":
                self.score_dict[winner] = "40"
                self.score_dict[loser] = "40"
            case "Ad":
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
        self.score_dict[self.us] = ""
        self.score_dict[self.them] = ""


    


