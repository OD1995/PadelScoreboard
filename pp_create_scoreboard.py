import win32com.client
from datetime import datetime

def get_media_created(path):
    shell = win32com.client.Dispatch("Shell.Application")
    folder = shell.Namespace(str(path.parent))
    item = folder.ParseName(path.name)

    # System.Media.DateEncoded
    raw_value = folder.GetDetailsOf(item, 208)

    if not raw_value:
        return None

    # Windows returns localized string → parse
    return datetime.strptime(raw_value, "%m/%d/%Y %I:%M %p")

from pathlib import Path

video = Path(r"C:\Users\odern\Downloads\IMG_5889.MOV")
media_created = get_media_created(video)
a=1

import json
from scoreboard import PadelPointerScoreboardGenerator 

JSON_PATH = r"D:\Dev\PadelScoreboard\data\padel_pointer_backup_2026-01-29_84332 amZ.json"
MATCH_IX = 1
OUTPUT_FOLDER = r"D:\Dev\PadelScoreboard\gifs"
VIDEO_FILE_PATH = r"C:\Users\odern\Downloads\IMG_5889.MOV"

with open(JSON_PATH) as f:
    js = json.load(f)

sg = PadelPointerScoreboardGenerator(
    js,
    match_ix=MATCH_IX,
    us_name=["ALEX","OLI"],
    them_name=["NIGEL","KUSHAGRA"],
    video_file_path=VIDEO_FILE_PATH
)

# sg.output_gif(OUTPUT_FOLDER)
sg.copy_analysis_df()

#ffmpeg -i "IMG_5897.mov" -c:v libx265 -vf "scale=1920:1080" -crf 23 -c:a copy -map_metadata 0 "1 Feb 26 Padel.mp4"
