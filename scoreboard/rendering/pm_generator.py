from .generator import ScoreboardGenerator
from ..dtos import MatchDto, SetDto, GameDto, PointDto
from datetime import datetime

class PadelMaxScoreboardGenerator(ScoreboardGenerator):

    def __init__(
        self,
        js,
        # match_ix,
        video_file_path
    ):
        ScoreboardGenerator.__init__(
            self=self,
            match=self.build_match(js['points'], js['info']['duration']['startTime']),
            deuces_allowed=self.get_deuces_allowed(js['info']['settings']),
            us_name="US",
            them_name='THEM',
            video_file_path=video_file_path
        )

    def build_match(self, points_js, start_timestamp) -> MatchDto:
        sets = []
        games = []
        points = []
        current_set = 1
        game_score = "0-0"
        for point_js in points_js:
            points.append(
                PointDto(
                    winner="us" if point_js['winner'] == "A" else "them",
                    serving_pair="us" if point_js['server'][0] == "A" else "them",
                    timestamp=datetime.fromisoformat(point_js['timestamp'].replace("Z", "+00:00"))
                )
            )
            is_new_set = point_js['currentSet'] != current_set
            is_new_game = point_js['games']['formatted'] != game_score
            if is_new_set or is_new_game:
                games.append(
                    GameDto(
                        points=points
                    )
                )
            
            if is_new_set:
                current_set = point_js['currentSet']
                sets.append(
                    SetDto(
                        games=games
                    )
                )
                games = []
            if is_new_game:
                game_score = point_js['games']['formatted']                
                points = []
                
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
            start_timestamp=datetime.fromisoformat(start_timestamp.replace("Z", "+00:00")),
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