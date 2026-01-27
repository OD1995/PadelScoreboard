import json
from scoreboard import PadelPointerScoreboardGenerator 

JSON_PATH = r"D:\Dev\PadelScoreboard\data\padel_pointer_backup_2026-01-26_105317 pmZ.json"
MATCH_IX = 0
OUTPUT_FOLDER = r"D:\Dev\PadelScoreboard\gifs"
VIDEO_FILE_PATH = r"D:\PadelVideos\Full Videos\26 Jan 26 Padel.mp4"

with open(JSON_PATH) as f:
    js = json.load(f)

sg = PadelPointerScoreboardGenerator(
    js,
    match_ix=MATCH_IX,
    us_name="ALEX\nOLI",
    them_name="ZYL\nGJT",
    video_file_path=VIDEO_FILE_PATH
)

# sg.output_gif(OUTPUT_FOLDER)
sg.copy_analysis_df()

#ffmpeg -i "IMG_5881.mov" -c:v libx265 -vf "scale=1920:1080" -crf 23 -c:a copy -map_metadata 0 "26 Jan 26 Padel.mp4"

## lessons
# 1 - Lex move to centre of court as I make diagonal run