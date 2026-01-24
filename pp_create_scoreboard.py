import json
from scoreboard import PadelPointerScoreboardGenerator 

JSON_PATH = r"D:\Dev\PadelScoreboard\data\padel_pointer_backup_2026-01-02_23646 pm.json"
MATCH_IX = 1
OUTPUT_FOLDER = r"D:\Dev\PadelScoreboard\gifs"

with open(JSON_PATH) as f:
    js = json.load(f)

sg = PadelPointerScoreboardGenerator(js, match_ix=MATCH_IX)

sg.output_gif(OUTPUT_FOLDER)