from .generator import ScoreboardGenerator
from ..dtos import MatchDto, SetDto, GameDto, PointDto
from datetime import datetime

class PadelMaxScoreboardGenerator(ScoreboardGenerator):

    def __init__(
        self,
        js,
        match_ix
    ):
        ScoreboardGenerator.__init__(
            self=self,
            match=self.build_match(js['points']),
            # sets=js['matches'][match_ix]['sets'],
            deuces_allowed=self.get_deuces_allowed(js['info']['settings']),
            us_name="US",
            them_name='THEM'
        )

    def build_match(self, points_js) -> MatchDto:
        sets = []
        games = []
        points = []
        current_set = 1
        game_score = "0-0"
        for point_js in points_js:
            if point_js['currentSet'] != current_set:
                current_set = point_js['currentSet']
                sets.append(
                    SetDto(
                        games=games
                    )
                )
                games = []
            if point_js['games']['formatted'] != game_score:
                game_score = point_js['games']['formatted']
                games.append(
                    GameDto(
                        points=points
                    )
                )
                points = []
            points.append(
                PointDto(
                    winner="us" if point_js['winner'] == "A" else "them",
                    serving_pair="us" if point_js['winner'][0] == "A" else "them",
                    timestamp=datetime.fromisoformat(point_js['timestamp'].replace("Z", "+00:00"))
                )
            )
        games.append(
            GameDto(
                points=points
            )
        )
        sets.append(
            SetDto(
                games=games
            )
        )
        return MatchDto(
            sets=sets
        )
    
    def get_deuces_allowed(self, deuce_format):
        # match deuce_format:
        #     case "classic":
        #         return 99
        #     case "goldenPoint":
        #         return 1
        #     case _:
        #         raise ValueError("Unexpected deuce format")
        if deuce_format['goldenPoint'] == 'Enabled':
            return 0
        return 99