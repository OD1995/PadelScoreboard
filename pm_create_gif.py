import json
from scoreboard import PadelMaxScoreboardGenerator 

JSON_PATH = r"D:\Dev\PadelScoreboard\data\match-e420c54b-38bc-4bbe-b08e-e6da8923e673-E420C54B-38BC-4BBE-B08E-E6DA8923E673.json"
MATCH_IX = 1
OUTPUT_FOLDER = r"D:\Dev\PadelScoreboard\gifs"

with open(JSON_PATH) as f:
    js = json.load(f)

sg = PadelMaxScoreboardGenerator(js, match_ix=MATCH_IX)

sg.output_gif(OUTPUT_FOLDER)