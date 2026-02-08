import json
from scoreboard import MultiMatchScoreboardGenerator
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import OrderedDict

JSON_PATH = r"D:\Dev\PadelScoreboard\data\padel_pointer_backup_2026-02-05_121526Z.json"
MATCH_IX = 1
OUTPUT_FOLDER = r"D:\Dev\PadelScoreboard\movs"
VIDEO_FILE_PATH = None#r"D:\PadelVideos\Full Videos\IMG_5924.MOV"
VIDEO_START = datetime(
    year=2026,
    month=2,
    day=4,
    hour=21,
    minute=2,
    second=12,
    tzinfo=ZoneInfo('Europe/London')
)
MATCH_PLAYERS = OrderedDict(
    [
        (
            1,
            {
                'us_name' : ["LARRY", "OLI"],
                'them_name' : ["DAN", "ALEX"]
            }
        ),
        (
            0,
            {
                'us_name' : ["OLI", "DAN"],
                'them_name' : ["ALEX", "LARRY"]
            }
        )
    ]
)
JUST_ANALYSIS = True

with open(JSON_PATH) as f:
    js = json.load(f)

dt = datetime.now().strftime("%d%b%y_%H%M%S")

sg = MultiMatchScoreboardGenerator(
    js=js,
    player_info=MATCH_PLAYERS,
    video_file_path=VIDEO_FILE_PATH,
    video_start=VIDEO_START,
    output_folder=fr"{OUTPUT_FOLDER}\{dt}"    
)

sg.output_scoreboard(just_analysis=JUST_ANALYSIS)