from PIL import Image, ImageDraw, ImageFont
from .games import GameHandler
from ..dtos import SetDto
from pathlib import Path

class SetHandler:

    def __init__(
        self,
        set: SetDto,
        set_ix,
        us_name,
        them_name,
        deuces_allowed,
        output_path2=None
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
    
    def get_match_states(self, sets_dicts, video_start):
        match_states = []
        for game_ix, game in enumerate(self.set.games):
            if not game.has_points():
                continue
            gh = GameHandler(game=game, deuces_allowed=self.deuces_allowed)
            is_first_point_of_match = ((game_ix == 0) and (self.set_ix == 0))
            game_scores, game_winner = gh.get_game_scores(is_first_point_of_match)
            for ix, game_score in enumerate(game_scores):
                if ix == len(game_scores) - 1:
                    self.games_counts[game_winner] += 1
                if not ((ix == 0) and is_first_point_of_match):
                    match_states.append(self.calculate_match_state(game_score, sets_dicts, video_start))
        return match_states
        
    def calculate_match_state(self, game_score, sets_dicts, video_start):
        return {
            "Game Score" : f"{game_score['us']}-{game_score['them']}",
            "Set Score" : self.calculate_set_score(sets_dicts),
            "Set Number" : self.set_ix + 1,
            "Video Timestamp" : self.calculate_video_timestamp(video_start, game_score['timestamp']),
            "Winner" : "A" if game_score['point_winner'] == "us" else "B",
            ## Use next_server if it's set (when game winning point has just happened)
            "Server" : "A" if game_score['server'] == "us" else "B"
        }
    
    def calculate_video_timestamp(self, video_start, event_time):
            delta = event_time - video_start
            total_seconds = max(0, int(delta.total_seconds()))
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def calculate_set_score(self, sets_dicts):
        # if len(sets_dicts) == 0:
        #     return None
        return ",".join([f"{sd['us']}-{sd['them']}" for sd in sets_dicts + [self.games_counts]])

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

        # ---------- logo ----------
        # logo_path = r"D:\Dev\PadelScoreboard\logos\PadelPointerWithTextV2.png"
        logo_path = (
            Path(__file__)
            .resolve()
            .parents[2]      # go up to project root
            / "logos"
            / "PadelPointerWithTextV2.png"
        )
        logo_img = Image.open(logo_path).convert("RGBA")

        scoreboard_width = cols * cell_width
        height = rows * cell_height

        # scale logo to fit height
        scale = height / logo_img.height
        logo_img = logo_img.resize(
            (int(logo_img.width * scale), height),
            Image.LANCZOS
        )
        logo_width = logo_img.width

        width = logo_width + scoreboard_width

        # ---------- transparent base image ----------
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # paste logo
        img.paste(logo_img, (0, 0), logo_img)

        x_offset = logo_width

        try:
            base_font_path = "arial.ttf"
            ImageFont.truetype(base_font_path, 28)
        except:
            base_font_path = None

        # ---------- helpers ----------

        def fill_cell_if_text(col, row, text, bg_color="white"):
            if text is None or text == "":
                return
            draw.rectangle(
                (
                    x_offset + col * cell_width,
                    row * cell_height,
                    x_offset + (col + 1) * cell_width,
                    (row + 1) * cell_height,
                ),
                fill=bg_color
            )

        def draw_centered_text(
            text,
            col,
            row,
            fill="black",
            max_font_size=28,
            min_font_size=12,
            padding=8
        ):
            if text is None or text == "":
                return

            x0 = x_offset + col * cell_width
            y0 = row * cell_height
            cell_w = cell_width - padding * 2
            cell_h = cell_height - padding * 2

            font_size = max_font_size

            while font_size >= min_font_size:
                try:
                    font = ImageFont.truetype(base_font_path, font_size) if base_font_path else ImageFont.load_default()
                except:
                    font = ImageFont.load_default()

                bbox = draw.multiline_textbbox(
                    (0, 0),
                    str(text),
                    font=font,
                    align="center"
                )

                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]

                if text_w <= cell_w and text_h <= cell_h:
                    break

                font_size -= 1

            x = x0 + (cell_width - text_w) // 2
            y = y0 + (cell_height - text_h) // 2

            draw.multiline_text(
                (x, y),
                str(text),
                fill=fill,
                font=font,
                align="center",
                spacing=2
            )

        # ---------- grid ----------
        for c in range(cols + 1):
            x = x_offset + c * cell_width
            draw.line((x, 0, x, height), fill="black", width=2)

        for r in range(rows + 1):
            y = r * cell_height
            draw.line((x_offset, y, x_offset + scoreboard_width, y), fill="black", width=2)

        # ---------- names + serving indicator ----------
        server = game_score.get("next_server") or game_score.get("server")
        serving_row = 0 if server == "us" else 1

        fill_cell_if_text(0, serving_row, self.us_name if serving_row == 0 else self.them_name, "#b6e7a7")
        fill_cell_if_text(0, 1 - serving_row, self.us_name if serving_row == 1 else self.them_name, "white")

        draw_centered_text(self.us_name, 0, 0)
        draw_centered_text(self.them_name, 0, 1)

        # ---------- set columns ----------
        for i, set_score in enumerate(sets_dicts):
            col = 1 + i

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
        if self.output_path2:
            img.save(
                fp=fr"{self.output_path2}\{set_ix}-{frame_ix}.png"
            )

        return img