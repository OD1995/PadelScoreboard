from ..scoring import SetHandler
from PIL import Image
from datetime import datetime
from pathlib import Path
from ..dtos import MatchDto
from ..timing import VideoTiming

class ScoreboardGenerator:

    def __init__(
        self,
        match:MatchDto,
        # sets,
        deuces_allowed,
        us_name,
        them_name,
        video_file_path
    ):
        self.match = match
        # self.sets = sets
        self.deuces_allowed = deuces_allowed
        self.us_name = us_name
        self.them_name = them_name
        self.video_timer = VideoTiming(video_file_path)

    def output_gif(self, output_path):
        dt = datetime.now().strftime("%d%b%y_%H%M%S")
        output_path2 = fr"{output_path}\{dt}"
        Path(output_path2).mkdir(parents=True, exist_ok=True)
        video_start = self.video_timer.get_video_start()
        sets_dicts = []
        all_frames = []
        for set_ix, set in enumerate(self.match.sets):
            if not set.has_points():
                continue
            sh = SetHandler(
                set=set,
                set_ix=set_ix,
                us_name=self.us_name,
                them_name=self.them_name,
                deuces_allowed=self.deuces_allowed,
                output_path2=output_path2
            )
            frames = sh.get_frames(sets_dicts)
            sets_dicts = sh.update_sets_dict(sets_dicts)
            all_frames.extend(frames)
        durations = self.get_durations()
        all_frames[0].save(
            fp=fr"{output_path2}\a.gif",
            append_images=all_frames[1:],
            duration=durations,
            loop=0
        )


    def get_base_image(self) -> Image:
        img = Image.new(
            mode="RGB",
            size=(500,300),
            color="white"
        )
        return img
    
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
        durations = list(reversed(durations_reversed))
        ## Show final score for 10 seconds
        durations.append(10*1000)
        return durations