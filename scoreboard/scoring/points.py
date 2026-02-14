from ..dtos import PointDto

class ScoreCalculator:

    def __init__(
        self,
        deuces_allowed: int,
        first_point: PointDto,
        us_name: str,
        them_name: str,
        match_stats: dict,
    ):        
        self.us_name = us_name
        self.them_name = them_name
        self.score_dict = {
            self.us_name : "0" if isinstance(self, NormalGameScoreCalculator) else 0,
            self.them_name : "0" if isinstance(self, NormalGameScoreCalculator) else 0,
            "server" : self.get_server(first_point),
            "next_server" : None
        }
        self.match_stats = match_stats
        ## Plus one to take into account the first time you reach 40-40
        self.deuces_allowed = deuces_allowed + 1
        self.deuce_count = 0
        self.game_winner = None
        self.point_history = []
        self.is_deciding_point = False

        self.GAME_NOT_STARTED_YET = "-"
        self.OPPONENT_ON_ADVANTAGE = "/"
        self.ADVANTAGE = "AD"

    def get_server(self, point:PointDto):
        us_server = point.serving_pair == "us"
        return self.us_name if us_server else self.them_name
    
    def get_returner(self, point:PointDto):
        us_server = point.serving_pair == "us"
        return self.us_name if (not us_server) else self.them_name
    
    def get_next_server(self, point:PointDto):
        us_server = point.serving_pair == "us"
        return self.them_name if us_server else self.us_name
    
    def get_winner(self, point:PointDto):
        us_winner = point.winner == "us"
        return self.us_name if us_winner else self.them_name
    
    def get_loser(self, point: PointDto):
        us_winner = point.winner == "us"
        return self.us_name if (not us_winner) else self.them_name

    def set_game_over(self, point_winner, point, is_deciding_point=False):
        self.game_winner = point_winner
        self.score_dict[self.us_name] = self.GAME_NOT_STARTED_YET
        self.score_dict[self.them_name] = self.GAME_NOT_STARTED_YET
        self.score_dict['next_server'] = self.get_next_server(point)
        if self.is_deciding_point:
            self.is_deciding_point = True

    def update_match_stats(
        self,
        point:PointDto,
        is_break_point:bool=False,
        is_converted_break_point:bool=False,
        is_deciding_point:bool=False,
        is_last_game_point:bool=False,
        is_last_set_point:bool=False
    ):
        self.match_stats[self.get_winner(point)]["pointsWon"] += 1
        if is_break_point:
            self.match_stats[self.get_returner(point)]["breakPoints"] += 1
        if is_converted_break_point:
            self.match_stats[self.get_returner(point)]["breakPointsConverted"] += 1
        if is_deciding_point:
            self.match_stats[self.get_winner(point)]["decidingPointsWon"] += 1
        if is_last_game_point:
            server_won = self.get_server(point) == self.get_winner(point)
            metric = "serviceGamesWon" if server_won else "returnGamesWon"
            self.match_stats[self.get_winner(point)]["gamesWon"] += 1
            self.match_stats[self.get_winner(point)][metric] += 1
        if is_last_set_point:
            self.match_stats[self.get_winner(point)]["setsWon"] += 1

class NormalGameScoreCalculator(ScoreCalculator):

    def __init__(
        self,
        deuces_allowed: int,
        first_point: PointDto,
        us_name: str,
        them_name: str,
        match_stats: dict,
    ):
        ScoreCalculator.__init__(
            self=self,
            deuces_allowed=deuces_allowed,
            first_point=first_point,
            us_name=us_name,
            them_name=them_name,
            match_stats=match_stats
        )        

    def add_point(
        self,
        point:PointDto,
        is_last_game_point:bool,
        is_last_set_point:bool
    ):
        self.point_history.append(point)
        self.score_dict['server'] = self.get_server(point)
        self.score_dict['point_winner'] = point.winner
        self.score_dict['timestamp'] = point.timestamp
        self.update_match_stats(
            point,
            is_break_point=self.get_is_break_point(point),
            is_converted_break_point=self.get_is_converted_break_point(point),
            is_deciding_point=self.get_is_deciding_point(point),
            is_last_game_point=is_last_game_point,
            is_last_set_point=is_last_set_point
        )
        winner = self.get_winner(point)
        loser = self.get_loser(point)
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
                        self.set_game_over(winner, point, True)
                else:
                    self.set_game_over(winner, point)
            case self.OPPONENT_ON_ADVANTAGE:
                self.score_dict[winner] = "40"
                self.score_dict[loser] = "40"
            case self.ADVANTAGE:
                self.set_game_over(winner, point)
        self.update_deuce_count()

    def get_is_break_point(self, point:PointDto):
        server = self.get_server(point)
        returner = self.get_returner(point)
        is_advantage = self.score_dict[returner] == self.ADVANTAGE
        is_40 = (self.score_dict[returner] == "40") and (self.score_dict[server] != "40")
        return is_advantage or is_40 or self.get_is_deciding_point(point)
    
    def get_is_converted_break_point(self, point:PointDto):
        return self.get_is_break_point(point) and (self.get_returner(point) == self.get_winner(point))
    
    def get_is_deciding_point(self, point:PointDto):
        return self.is_deciding_point

    def update_deuce_count(self):
        us_40 = self.score_dict[self.us_name] == "40"
        tied = self.score_dict[self.us_name] == self.score_dict[self.them_name]
        if us_40 and tied:
            self.deuce_count += 1

class TiebreakGameScoreCalculator(ScoreCalculator):

    def __init__(
        self,
        deuces_allowed:int,
        first_point:PointDto,
        us_name:str,
        them_name:str,
        match_stats:dict,
    ):
        ScoreCalculator.__init__(
            self=self,
            deuces_allowed=deuces_allowed,
            first_point=first_point,
            us_name=us_name,
            them_name=them_name,
            match_stats=match_stats
        )        

    def add_point(self, point:PointDto):
        self.point_history.append(point)        
        self.score_dict['server'] = self.get_server(point)
        if len(self.point_history) % 2 == 1:
            self.score_dict['next_server'] = self.get_next_server(point)
        self.score_dict['point_winner'] = point.winner
        self.score_dict['timestamp'] = point.timestamp
        winner = self.get_winner(point)
        loser = self.get_loser(point)
        if (self.score_dict[winner] < 6) or (self.score_dict[winner] - self.score_dict[loser] != 1):
            self.score_dict[winner] = self.score_dict[winner] + 1
        else:
            self.set_game_over(winner, point)
        self.update_match_stats(point)