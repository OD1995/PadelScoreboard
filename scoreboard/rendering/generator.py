from ..scoring import SetHandler
from PIL import Image
from datetime import datetime
from pathlib import Path
from ..dtos import MatchDto

class ScoreboardGenerator:

    def __init__(
        self,
        match:MatchDto,
        # sets,
        deuces_allowed,
        us_name,
        them_name
    ):
        self.match = match
        # self.sets = sets
        self.deuces_allowed = deuces_allowed
        self.us_name = us_name
        self.them_name = them_name

    def output_gif(self, output_path):
        dt = datetime.now().strftime("%d%b%y_%H%M%S")
        output_path2 = fr"{output_path}\{dt}"
        Path(output_path2).mkdir(parents=True, exist_ok=True)
        sets_dicts = []
        all_frames = []
        all_durations = []
        for set in self.match.sets:
            sh = SetHandler(
                set=set,
                us_name=self.us_name,
                them_name=self.them_name,
                deuces_allowed=self.deuces_allowed,
                output_path2=output_path2
            )
            frames,durations = sh.get_frames_and_durations(sets_dicts)
            sets_dicts = sh.update_sets_dict(sets_dicts)
            all_frames.extend(frames)
            all_durations.extend(durations)
        all_frames[0].save(
            fp=fr"{output_path2}\a.gif",
            append_images=all_frames[1:],
            duration=all_durations,
            loop=0
        )


    def get_base_image(self) -> Image:
        img = Image.new(
            mode="RGB",
            size=(500,300),
            color="white"
        )
        return img