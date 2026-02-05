import json
from scoreboard import PadelPointerScoreboardGenerator
from datetime import datetime
import pytz

JSON_PATH = r"D:\Dev\PadelScoreboard\data\padel_pointer_backup_2026-02-03_113056 amZ.json"
MATCH_IX = 1
OUTPUT_FOLDER = r"D:\Dev\PadelScoreboard\gifs"
VIDEO_FILE_PATH = None
VIDEO_START = datetime(
    year=2026,
    month=2,
    day=2,
    hour=9,
    minute=3,
    second=31,
    tzinfo=pytz.timezone('Europe/London')
)

with open(JSON_PATH) as f:
    js = json.load(f)

sg = PadelPointerScoreboardGenerator(
    js,
    match_ix=MATCH_IX,
    us_name=["ALEX","OLI"],
    them_name=["JAMES","JEREMY"],
    video_file_path=VIDEO_FILE_PATH,
    video_start=VIDEO_START,
    video_end=None,
    video_duration=None
)

sg.output_gif(OUTPUT_FOLDER)
# sg.copy_analysis_df()

#ffmpeg -i "IMG_5897.mov" -c:v libx265 -vf "scale=1920:1080" -crf 23 -c:a copy -map_metadata 0 "1 Feb 26 Padel.mp4"
