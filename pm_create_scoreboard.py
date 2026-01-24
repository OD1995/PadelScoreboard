import json
from scoreboard import PadelMaxScoreboardGenerator
from scoreboard.timing import VideoTiming

JSON_PATH = r"D:\Dev\PadelScoreboard\data\match-e420c54b-38bc-4bbe-b08e-e6da8923e673-E420C54B-38BC-4BBE-B08E-E6DA8923E673.json"
MATCH_IX = 1
OUTPUT_FOLDER = r"D:\Dev\PadelScoreboard\mp4s"
VIDEO_FILE_PATH = r"D:\PadelVideos\Full Videos\IMG_5834.MOV"

with open(JSON_PATH) as f:
    js = json.load(f)

sg = PadelMaxScoreboardGenerator(
    js=js,
    us_name="ALEX\nOLI",
    them_name="PETR\nMUHAMMED",
    video_file_path=VIDEO_FILE_PATH
)

sg.output_gif(OUTPUT_FOLDER)
sg.copy_analysis_df()