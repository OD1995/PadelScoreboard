import json
from scoreboard import MultiMatchScoreboardGenerator
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import OrderedDict

JSON_PATH = r"D:\Dev\PadelScoreboard\data\padel_pointer_backup_2026-01-29_84332 amZ.json"
OUTPUT_FOLDER = r"D:\Dev\PadelScoreboard\movs"
VIDEO_FILE_PATH = r"D:\PadelVideos\Full Videos\28 Jan 26 Padel Original.mp4"
VIDEO_START = None
# VIDEO_START = datetime(
#     year=2026,
#     month=2,
#     day=2,
#     hour=21,
#     minute=3,
#     second=31,
#     tzinfo=ZoneInfo('Europe/London')
# )
MATCH_PLAYERS = OrderedDict(
    [
        (
            1,
            {
                'us_name' : ("ALEX", "OLI"),
                'them_name' : ("NIGEL", "KUSHAGRA")
            }
        ),
        (
            0,
            {
                'us_name' : ("ALEX", "OLI"),
                'them_name' : ("NIGEL", "KUSHAGRA")
            }
        )
    ]
)
JUST_ANALYSIS = False

with open(JSON_PATH) as f:
    js = json.load(f)

dt = datetime.now().strftime("%d%b%y_%H%M%S")

sg = MultiMatchScoreboardGenerator(
    js=js,
    player_info=MATCH_PLAYERS,
    video_file_path=VIDEO_FILE_PATH,
    video_start=VIDEO_START,
    output_folder=fr"{OUTPUT_FOLDER}\{dt}",
    just_analysis=JUST_ANALYSIS
)

sg.output_scoreboard()

# sets won
# games won
# service games won
# return games won
# points won
# break point conversion %
# golden points won

## height (total) - 2.25 (14.25) 15%
# scoreboard height - 15%
# stats table height - 75%
# stats table width - 60%