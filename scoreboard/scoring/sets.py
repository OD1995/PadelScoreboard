from .games import GameHandler
from ..dtos import SetDto
from ..drawing import ScoreboardImageDrawer
from PIL import Image
from datetime import datetime

class SetHandler:

    def __init__(
        self,
        set:SetDto,
        set_ix,
        is_last_set_of_match:bool,
        us_name,
        them_name,
        deuces_allowed,
        output_path2=None,
        just_analysis=False
    ):
        self.set = set
        self.set_ix = set_ix
        self.is_last_set_of_match = is_last_set_of_match
        self.us_name = us_name
        self.them_name = them_name
        self.deuces_allowed = deuces_allowed
        self.output_path2 = output_path2
        self.games_counts = {
            self.us_name : 0,
            self.them_name : 0
        }
        self.sid = ScoreboardImageDrawer(
            us_name=self.us_name,
            them_name=self.them_name,
            just_analysis=just_analysis
        )

    def get_empty_opening_frame(self):
        return self.sid.get_empty_opening_frame()
    
    def get_frames_and_match_states(self, sets_dicts, video_start, match_stats):
        # print(f"{datetime.now()} - get_frames_and_match_states init")
        frames = []
        match_states = []
        for game_ix, game in enumerate(self.set.games):
            if not game.has_points():
                continue
            gh = GameHandler(
                game=game,
                us_name=self.us_name,
                them_name=self.them_name,
                deuces_allowed=self.deuces_allowed,
                match_stats=match_stats,
            )
            is_first_point_of_match = ((game_ix == 0) and (self.set_ix == 0))
            is_last_game_of_set = game_ix == len(self.set.games) - 1
            game_scores, game_winner, match_stats_array = gh.get_game_scores(
                is_first_point_of_match=is_first_point_of_match,
                is_last_game_of_set=is_last_game_of_set
            )
            for ix, game_score in enumerate(game_scores):
                if ix == len(game_scores) - 1:
                    self.games_counts[game_winner] += 1
                if not ((ix == 0) and is_first_point_of_match):
                    match_states.append(self.calculate_match_state(game_score, sets_dicts, video_start))
                is_last_point_of_game = ix == len(game_scores) - 1
                is_last_point_of_set = is_last_point_of_game and is_last_game_of_set
                is_last_point_of_match = is_last_point_of_game and is_last_game_of_set and self.is_last_set_of_match
                if is_last_point_of_set:
                    frames.append(
                        self.sid.generate_whole_screen_image(
                            sets_dicts=[*sets_dicts, self.games_counts],
                            game_score=game_score,
                            match_stats=match_stats_array[ix],
                            display_stats_table=True
                        )
                    )
                if not is_last_point_of_match:
                    frames.append(
                        self.sid.generate_whole_screen_image(
                            sets_dicts=[*sets_dicts, self.games_counts],
                            game_score=game_score,
                            match_stats=match_stats_array[ix]
                        )
                    )
        return frames, match_stats_array[-1]

    def update_sets_dict(self, sets_dicts):
        return sets_dicts + [self.games_counts]
    
    # def get_match_states(self, sets_dicts, video_start):
    #     match_states = []
    #     for game_ix, game in enumerate(self.set.games):
    #         if not game.has_points():
    #             continue
    #         gh = GameHandler(
    #             game=game,
    #             deuces_allowed=self.deuces_allowed,

    #         )
    #         is_first_point_of_match = ((game_ix == 0) and (self.set_ix == 0))
    #         game_scores, game_winner = gh.get_game_scores(is_first_point_of_match)
    #         for ix, game_score in enumerate(game_scores):
    #             if ix == len(game_scores) - 1:
    #                 self.games_counts[game_winner] += 1
    #             if not ((ix == 0) and is_first_point_of_match):
    #                 match_states.append(self.calculate_match_state(game_score, sets_dicts, video_start))
    #     return match_states
        
    def calculate_match_state(self, game_score, sets_dicts, video_start):
        return {
            "Game Score" : f"{game_score[self.us_name]}-{game_score[self.them_name]}",
            "Set Score" : self.calculate_set_score(sets_dicts),
            "Set Number" : self.set_ix + 1,
            "Video Timestamp" : self.calculate_video_timestamp(video_start, game_score['timestamp']),
            "Winner" : "A" if game_score['point_winner'] == self.us_name else "B",
            ## Use next_server if it's set (when game winning point has just happened)
            "Server" : "A" if game_score['server'] == self.us_name else "B"
        }
    
    def calculate_video_timestamp(self, video_start, event_time):
            delta = event_time - video_start
            total_seconds = max(0, int(delta.total_seconds()))
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def calculate_set_score(self, sets_dicts):
        # if len(sets_dicts) == 0:
        #     return None
        return ",".join([f"{sd[self.us_name]}-{sd[self.them_name]}" for sd in sets_dicts + [self.games_counts]])