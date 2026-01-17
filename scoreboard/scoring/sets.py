from PIL import Image, ImageDraw, ImageFont
from .games import GameHandler
from ..dtos import SetDto


class SetHandler:

    def __init__(
        self,
        set: SetDto,
        set_ix,
        us_name,
        them_name,
        deuces_allowed,
        output_path2
    ):
        self.set = set
        self.set_ix = set_ix
        self.us_name = us_name
        self.them_name = them_name
        self.deuces_allowed = deuces_allowed
        self.output_path2 = output_path2
        self.games_counts = {
            "us": 0,
            "them": 0
        }

    def get_frames(self, sets_dicts):
        frames = []
        for game_ix, game in enumerate(self.set.games):
            if not game.has_points():
                continue
            gh = GameHandler(game=game, deuces_allowed=self.deuces_allowed)
            game_scores, game_winner = gh.get_game_scores(
                is_first_point_of_match=((game_ix == 0) and (self.set_ix == 0))
            )
            for ix, game_score in enumerate(game_scores):
                if ix == len(game_scores) - 1:
                    self.games_counts[game_winner] += 1
                frames.append(
                    self.generate_scoreboard_image(
                        sets_dicts=[*sets_dicts, self.games_counts],
                        game_score=game_score,
                        set_ix=len(sets_dicts),
                        frame_ix=len(frames)
                    )
                )
        return frames

    def update_sets_dict(self, sets_dicts):
        return sets_dicts + [self.games_counts]

    def generate_scoreboard_image(
        self,
        sets_dicts: list,
        game_score: dict,
        cell_width: int = 120,
        cell_height: int = 80,
        set_ix=0,
        frame_ix=0
    ):
        cols = 2 + len(sets_dicts)
        rows = 2

        width = 5 * cell_width
        height = rows * cell_height

        # ---------- transparent base image ----------
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()

        # ---------- helpers ----------

        def fill_cell_if_text(col, row, text, bg_color="white"):
            if text not in (None, ""):
                draw.rectangle(
                    (
                        col * cell_width,
                        row * cell_height,
                        (col + 1) * cell_width,
                        (row + 1) * cell_height,
                    ),
                    fill=bg_color
                )

        def draw_centered_text(text, col, row, fill="black"):
            x0 = col * cell_width
            y0 = row * cell_height

            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            x = x0 + (cell_width - text_w) // 2
            y = y0 + (cell_height - text_h) // 2

            draw.text((x, y), text, fill=fill, font=font)

        # ---------- grid ----------
        for c in range(cols + 1):
            x = c * cell_width
            draw.line((x, 0, x, height), fill="black", width=2)

        for r in range(rows + 1):
            y = r * cell_height
            draw.line((0, y, cols * cell_width, y), fill="black", width=2)

        # ---------- names ----------
        # ---------- serving indicator ----------
        serving_row = 0 if game_score.get("server") == "us" else 1
        fill_cell_if_text(0, serving_row, self.us_name if serving_row == 0 else self.them_name, "#b6e7a7")
        fill_cell_if_text(0, 1 if game_score.get("server") == "us" else 0, self.us_name, "white")
        draw_centered_text(self.us_name, 0, 0)
        draw_centered_text(self.them_name, 0, 1)


        # ---------- set columns (BLACK BG, WHITE TEXT) ----------
        for i, set_score in enumerate(sets_dicts):
            col = 1 + i

            # only fill if score exists
            fill_cell_if_text(col, 0, set_score.get("us"), "black")
            fill_cell_if_text(col, 1, set_score.get("them"), "black")

            draw_centered_text(str(set_score.get("us", "")), col, 0, fill="white")
            draw_centered_text(str(set_score.get("them", "")), col, 1, fill="white")

        # ---------- current game score ----------
        last_col = cols - 1

        fill_cell_if_text(last_col, 0, game_score.get("us"), "white")
        fill_cell_if_text(last_col, 1, game_score.get("them"), "white")

        draw_centered_text(str(game_score.get("us", "")), last_col, 0)
        draw_centered_text(str(game_score.get("them", "")), last_col, 1)

        # ---------- save frame ----------
        img.save(
            fp=fr"{self.output_path2}\{set_ix}-{frame_ix}.png"
        )

        return img