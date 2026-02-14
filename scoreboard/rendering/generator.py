from ..scoring import SetHandler
from datetime import datetime, timedelta
from pathlib import Path
from ..dtos import MatchDto
from ..timing import VideoTiming
import os
import subprocess
import pandas as pd

class ScoreboardGenerator:

    def __init__(
        self,
        match:MatchDto,
        # sets,
        deuces_allowed,
        us_name,
        them_name,
        video_file_path=None,
        video_start=None,
        video_end=None,
        video_duration=None,
        just_analysis=False
    ):
        self.match = match
        # self.sets = sets
        self.deuces_allowed = deuces_allowed
        self.us_name = us_name
        self.them_name = them_name
        self.video_timer = VideoTiming(video_file_path) \
            if video_file_path is not None \
            else None
        self.video_start = video_start
        self.video_end = video_end
        self.video_duration = video_duration
        self.just_analysis = just_analysis
    

    def get_video_start(self):
        if self.video_start is not None:
            return self.video_start
        if self.video_timer is not None:
            return self.video_timer.get_video_start()
        raise ValueError('logic required here')
    

    def build_video_and_get_analysis_df(self, output_path, starting_i, create_mov, video_start_override):
        print(f"{datetime.now()} - build_video_and_get_analysis_df")
        Path(output_path).mkdir(parents=True, exist_ok=True)
        sets_dicts = []
        all_frames = []
        match_metrics = [
            "setsWon",
            "gamesWon",
            "serviceGamesWon",
            "returnGamesWon",
            "pointsWon",
            "breakPoints",
            "breakPointsConverted",
            "decidingPointsWon",
        ]
        match_stats = {
            pair : {metric : 0 for metric in match_metrics}
            for pair in [self.us_name, self.them_name]
        }
        rows = []
        sets_dicts = []
        for set_ix, set in enumerate(self.match.sets):
            if not set.has_points():
                continue
            sh = SetHandler(
                set=set,
                set_ix=set_ix,
                us_name=self.us_name,
                them_name=self.them_name,
                deuces_allowed=self.deuces_allowed,
                # output_path2=output_path2
                just_analysis=self.just_analysis
            )
            if set_ix == 0:
                all_frames.append(sh.get_empty_opening_frame())
            frames, set_rows = sh.get_frames_and_match_states(
                sets_dicts=sets_dicts,
                video_start=video_start_override or self.get_video_start(),
                match_stats=match_stats
            )
            sets_dicts = sh.update_sets_dict(sets_dicts)
            all_frames.extend(frames)
            rows.extend(set_rows)
        durations = self.get_durations()
        self.create_mp4(
            output_path=output_path,
            frames=all_frames,
            durations=durations,
            starting_i=starting_i,
            create_mov=create_mov
        )
        df = pd.DataFrame(rows)
        new_video_start = self.get_video_start() + timedelta(seconds=sum(durations)/1000)
        new_starting_i = starting_i + len(all_frames)
        return new_video_start, new_starting_i, df
        

    def create_mp4(
        self,
        output_path,
        frames,
        durations,
        starting_i=0,
        create_mov=True
        # temp_dir="temp_frames"
    ):
        """
        Create an MP4 from a list of PIL.Image objects with per-frame durations using FFmpeg.

        Parameters:
            images: List of PIL.Image objects
            durations: List of float, duration of each frame in seconds
            output_path: Path to the final MP4
            temp_dir: Temporary directory to store frames
        """
        temp_dir = output_path
        # 1️⃣ Create temporary folder
        os.makedirs(temp_dir, exist_ok=True)

        # 2️⃣ Save each frame as a PNG
        frame_files = []
        for i, img in enumerate(frames, starting_i):
            frame_path = os.path.join(temp_dir, f"frame_{i:06d}.png")
            img.save(frame_path)
            frame_files.append(frame_path)

        # 3️⃣ Create FFmpeg concat list
        concat_file_path = os.path.join(temp_dir, "frames.txt")
        with open(concat_file_path, "a") as f:
            for frame, duration in zip(frame_files, durations):
                f.write(f"file '{os.path.abspath(frame)}'\n")
                f.write(f"duration {duration/1000}\n")
            if create_mov:
                # FFmpeg requires the last file repeated without duration
                f.write(f"file '{os.path.abspath(frame_files[-1])}'\n")

        # 4️⃣ Call FFmpeg
        # ffmpeg_cmd = [
        #     "ffmpeg",
        #     "-f", "concat",
        #     "-safe", "0",
        #     "-i", concat_file_path,
        #     # "-vsync", "vfr",            # variable frame rate
        #     "-c:v", "libvpx-vp9", 
        #     "-pix_fmt", "yuva420p",
        #     # "-movflags", "+faststart",   # optional: helps playback in editors
        #     fr"{output_path}\a.webm"
        # ] #-c:v prores -pix_fmt yuva444p10le logo.mov
        #ffmpeg -f concat -safe 0 -i frames.txt -vf format=yuva444p -c:v prores_ks -profile:v 4444 a_alpha.mov
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file_path,
            "-vf", "format=yuva444p",
            "-c:v", "prores_ks", 
            "-profile:v", "4444",
            fr"{output_path}\a_alpha.mov"
        ] # works but weird playback

        if create_mov:          
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Video saved to {output_path}")


    def create_gif(self, output_path, frames, durations):
        frames[0].save(
            fp=fr"{output_path}\a.gif",
            append_images=frames[1:],
            duration=durations,
            loop=0
        )

    
    def get_durations(self) -> list[int]:
        timestamps = [self.match.start_timestamp]
        for set in self.match.sets:
            for game in set.games:
                timestamps.extend(
                    [p.timestamp for p in game.points]
                )
        durations_reversed = []
        last_timestamp = timestamps[-1]
        for ts in reversed(timestamps[:-1]):
            durations_reversed.append(int((last_timestamp - ts).total_seconds() * 1000))
            last_timestamp = ts
        # ## Have empty frame from video start to match start
        video_start = self.get_video_start()
        durations_reversed.append(int((last_timestamp - video_start).total_seconds() * 1000)) #07:45
        durations = list(reversed(durations_reversed))
        ## Show final score for 10 seconds
        durations.append(10*1000)
        return durations
    
    
    # def copy_analysis_df(self):
    #     df = self.get_analysis_df()
    #     df.to_clipboard(index=False, header=None)

    # def get_analysis_df(self, video_start_override=None):
    #     rows = []
    #     sets_dicts = []
    #     for set_ix, set in enumerate(self.match.sets):
    #         if not set.has_points():
    #             continue
    #         sh = SetHandler(
    #             set=set,
    #             set_ix=set_ix,
    #             us_name=self.us_name,
    #             them_name=self.them_name,
    #             deuces_allowed=self.deuces_allowed
    #         )
    #         set_rows = sh.get_match_states(sets_dicts, video_start_override or self.get_video_start())
    #         sets_dicts = sh.update_sets_dict(sets_dicts)
    #         rows.extend(set_rows)
    #     df = pd.DataFrame(rows)
    #     return df