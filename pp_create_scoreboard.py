import json
from scoreboard import PadelPointerScoreboardGenerator
from datetime import datetime
import pytz

JSON_PATH = r"D:\Dev\PadelScoreboard\data\padel_pointer_backup_2026-02-05_121526Z.json"
MATCH_IX = 1
OUTPUT_FOLDER = r"D:\Dev\PadelScoreboard\gifs"
VIDEO_FILE_PATH = r"D:\PadelVideos\Full Videos\IMG_5924.MOV"
VIDEO_START = None#datetime(
#     year=2026,
#     month=2,
#     day=2,
#     hour=9,
#     minute=3,
#     second=31,
#     tzinfo=pytz.timezone('Europe/London')
# )
MATCH_PLAYERS = {
    1 : {
        'us_name' : ["LARRY", "OLI"],
        'them_name' : ["DAN", "ALEX"]
    },
    0 : {
        'us_name' : ["OLI", "DAN"],
        'them_name' : ["ALEX", "LARRY"]
    }
}

with open(JSON_PATH) as f:
    js = json.load(f)

if len(MATCH_PLAYERS) > 0:
    for i, (match_ix, name_info) in enumerate(MATCH_PLAYERS.items()):
        sg = PadelPointerScoreboardGenerator(
            js,
            match_ix=match_ix,
            us_name=name_info['us_name'],
            them_name=name_info['them_name'],
            video_file_path=VIDEO_FILE_PATH,
            video_start=VIDEO_START,
            video_end=None,
            video_duration=None,
            multi_match=i
        )
        sg.output_gif(OUTPUT_FOLDER)

else:
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
