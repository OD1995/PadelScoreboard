from .generator import ScoreboardGenerator
from ..dtos import MatchDto, SetDto, GameDto, PointDto
from datetime import datetime


class PadelPointerScoreboardGenerator(ScoreboardGenerator):

    def __init__(
        self,
        js,
        match_ix
    ):
        ScoreboardGenerator.__init__(
            self=self,
            match=self.build_match(js, match_ix),
            # sets=js['matches'][match_ix]['sets'],
            deuces_allowed=self.get_deuces_allowed(js['matches'][match_ix]['pointsFormat']),
            us_name="US",
            them_name='THEM'
        )
    
    def build_match(self, js, match_ix) -> MatchDto:
        sets = []
        for set_js in js['matches'][match_ix]['sets']:
            games = []
            for game_js in set_js['games']:
                points = []
                for point_js in game_js['points']:
                    points.append(
                        PointDto(
                            winner="us" if point_js['winner'] == "you" else "them",
                            serving_pair="us" if point_js['server'] == "you" else "them",
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
        match deuce_format:
            case "classic":
                return 99
            case "goldenPoint":
                return 1
            case _:
                raise ValueError("Unexpected deuce format")