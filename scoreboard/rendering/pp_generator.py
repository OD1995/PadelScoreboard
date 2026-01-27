from .generator import ScoreboardGenerator
from ..dtos import MatchDto, SetDto, GameDto, PointDto
from datetime import datetime


class PadelPointerScoreboardGenerator(ScoreboardGenerator):

    def __init__(
        self,
        js,
        match_ix,
        us_name,
        them_name,
        video_file_path
    ):
        ScoreboardGenerator.__init__(
            self=self,
            match=self.build_match(js['matches'][match_ix]),
            # sets=js['matches'][match_ix]['sets'],
            deuces_allowed=self.get_deuces_allowed(js['matches'][match_ix]['pointsFormat']),
            us_name=us_name,
            them_name=them_name,
            video_file_path=video_file_path
        )
    
    def build_match(self, match_js) -> MatchDto:
        sets = []
        for set_js in match_js['sets']:
            games = []
            for game_js in set_js['games']:
                points = []
                for point_js in game_js['points']:
                    points.append(
                        PointDto(
                            winner="us" if point_js['winner'] == "user" else "them",
                            serving_pair="us" if point_js['server'] in ["user","partner"] else "them",
                            timestamp=datetime.fromisoformat(point_js['timestamp'].replace("Z", "+00:00"))
                        )
                    )
                games.append(
                    GameDto(
                        points=points,
                        is_tiebreak=False
                    )
                )
            if set_js['isTiebreak']:
                tiebreak_points = []
                for tiebreak_point_js in set_js['tiebreakScore']['points']:
                    tiebreak_points.append(
                        PointDto(
                            winner="us" if tiebreak_point_js['winner'] == "user" else "them",
                            serving_pair="us" if tiebreak_point_js['server'] in ["user","partner"] else "them",
                            timestamp=datetime.fromisoformat(tiebreak_point_js['timestamp'].replace("Z", "+00:00"))
                        )
                    )
                games.append(
                    GameDto(
                        points=tiebreak_points,
                        is_tiebreak=True
                    )
                )

            sets.append(
                SetDto(
                    games=games
                )
            )
        return MatchDto(
            start_timestamp=datetime.fromisoformat(match_js['startTime'].replace("Z", "+00:00")),
            sets=sets
        )

    def get_deuces_allowed(self, deuce_format):
        match deuce_format:
            case "classic":
                return 99
            case "goldenPoint":
                return 1
            case _:
                raise ValueError("Unexpected deuce format")