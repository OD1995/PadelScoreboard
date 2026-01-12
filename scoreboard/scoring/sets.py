from PIL import Image, ImageDraw, ImageFont
from .games import GameHandler
from ..dtos import SetDto

class SetHandler:

    def __init__(
        self,
        set:SetDto,
        us_name,
        them_name,
        deuces_allowed,
        output_path2
    ):
        self.set = set
        self.us_name = us_name
        self.them_name = them_name
        self.deuces_allowed = deuces_allowed
        # self.us_sets = us_sets
        # self.them_sets = them_sets
        self.output_path2 = output_path2
        self.games_counts = {
            "us" : 0,
            "them" : 0
        }

    def get_frames_and_durations(self, sets_dicts):
        frames = []
        for game in self.set.games:
            gh = GameHandler(game=game, deuces_allowed=self.deuces_allowed)
            game_scores, game_winner = gh.get_game_scores()
            for ix, game_score in enumerate(game_scores):
                if ix == len(game_scores) - 1:
                    self.games_counts[game_winner] += 1
                frames.append(
                    self.generate_scoreboard_image(
                        sets_dicts=[*sets_dicts,self.games_counts],
                        game_score=game_score,
                        # us_serving=gh.us_serving,
                        set_ix=len(sets_dicts),
                        frame_ix=len(frames)
                    )
                )
        return frames, [500 for f in frames]
    
    def update_sets_dict(self, sets_dicts):
        return sets_dicts + [self.games_counts]

    def generate_scoreboard_image(
        self,
        sets_dicts: list,
        # us_game_score: str,
        # them_game_score: str,
        game_score: dict,
        # us_serving: bool,
        cell_width: int = 120,
        cell_height: int = 80,
        set_ix=0,
        frame_ix=0
    ):
        cols = 2 + len(sets_dicts)
        rows = 2

        width = 5 * cell_width
        height = rows * cell_height

        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()

        # Helper for centered text
        def draw_centered_text(text, col, row):
            x0 = col * cell_width
            y0 = row * cell_height

            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            x = x0 + (cell_width - text_w) // 2
            y = y0 + (cell_height - text_h) // 2

            draw.text((x, y), text, fill="black", font=font)

        # 🟩 Serving indicator (background fill)
        serving_row = 0 if game_score['server'] == "us" else 1
        draw.rectangle(
            (
                0,
                serving_row * cell_height,
                cell_width,
                (serving_row + 1) * cell_height
            ),
            fill="#b6e7a7"  # soft green
        )

        # Draw grid
        for c in range(cols + 1):
            x = c * cell_width
            draw.line((x, 0, x, height), fill="black", width=2)

        for r in range(rows + 1):
            y = r * cell_height
            draw.line((0, y, cols * cell_width, y), fill="black", width=2)

        # Column 0: names
        draw_centered_text(self.us_name, 0, 0)
        draw_centered_text(self.them_name, 0, 1)

        # Set columns
        for i, set_score in enumerate(sets_dicts):
            col = 1 + i
            draw_centered_text(str(set_score["us"]), col, 0)
            draw_centered_text(str(set_score["them"]), col, 1)

        # Last column: current game score
        last_col = cols - 1
        draw_centered_text(str(game_score["us"]), last_col, 0)
        draw_centered_text(str(game_score["them"]), last_col, 1)

        img.save(
            fp=fr"{self.output_path2}\{set_ix}-{frame_ix}.png"
        )

        return img
