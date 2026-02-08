from collections import OrderedDict
from .pp_generator import PadelPointerScoreboardGenerator
from datetime import datetime
import pandas as pd

class MultiMatchScoreboardGenerator:

    def __init__(
        self,
        js:dict,
        player_info:OrderedDict,
        video_file_path:str,
        video_start:datetime,
        output_folder:str
    ):
        self.js = js
        self.player_info = player_info
        self.video_file_path = video_file_path
        self.video_start = video_start
        self.output_folder = output_folder

    def output_scoreboard(self, just_analysis):
        starting_i = 0
        video_start = self.video_start
        dfs = []
        for i, (match_ix, name_info) in enumerate(self.player_info.items()):
            sg = PadelPointerScoreboardGenerator(
                self.js,
                match_ix=match_ix,
                us_name=name_info['us_name'],
                them_name=name_info['them_name'],
                video_file_path=self.video_file_path,
                video_start=video_start,
                video_end=None,
                video_duration=None
            )
            video_start, starting_i = sg.build_video(
                output_path=self.output_folder,
                starting_i=starting_i,
                create_mov=(i == len(self.player_info) - 1)
            )
            df = sg.get_analysis_df(None if i == 0 else self.video_start)
            dfs.append(df)
        combined_df = pd.concat(dfs)
        combined_df.to_excel(fr"{self.output_folder}/analysis.xlsx")