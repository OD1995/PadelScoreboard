from PIL import Image, ImageDraw, ImageFont
from ..dtos import ScoreboardCellInfoDto
from pathlib import Path

class ScoreboardImageDrawer:

    def __init__(
        self,
        us_name,
        them_name
    ):
        self.us_name = us_name
        self.them_name = them_name

        try:
            self.base_font_path = "arial.ttf"
            ImageFont.truetype(self.base_font_path, 28)
        except:
            self.base_font_path = None

        ## Both will get overwritten later
        self.sets_dicts = []
        self.game_score = {}

        self.multiplier = 1


        self.widths = {
            'logo' : 120 * self.multiplier,
            'player_names' : self.calculate_player_name_width() * self.multiplier,
            'set_games' : 50 * self.multiplier,
            'game_scores' : 60 * self.multiplier,
        }
        self.cell_height = 60 * self.multiplier
        self.font_size = 20 * self.multiplier

    def calculate_player_name_width(self):
        width = 0
        for name in [self.us_name, self.them_name]:
            if isinstance(name, list):
                for nm in name:
                    width = max(width, self.width_calc(nm))
            else:
                width = max(width, self.width_calc(name))
        return width

    def width_calc(self, name):
        return (len(name)*20) + 5
    
    def calculate_scoreboard_width(self, widths):
        return (
            widths['logo'] +
            (widths['set_games'] * 3) +
            widths['game_scores'] +
            widths['player_names']
        )
    
    def get_cell_widths(self):
        cell_widths = [
            self.widths['logo'],
            self.widths['player_names']
        ]
        for i in self.sets_dicts:
            cell_widths.append(self.widths['set_games'])
        cell_widths.append(self.widths['game_scores'])
        return cell_widths
    
    def get_cumulative_cell_widths(self):
        prev_val = 0
        cumulative_cell_widths = []
        for w in self.get_cell_widths():
            prev_val += w
            cumulative_cell_widths.append(prev_val)
        return cumulative_cell_widths

    def draw_centered_text(self, draw:ImageDraw, cell_info:ScoreboardCellInfoDto):
        if (cell_info.text is None) or (cell_info.text == ""):
            return
        draw.multiline_text(
            xy=cell_info.get_middle_of_cell(self.get_cumulative_cell_widths()),
            text=str(cell_info.text),
            fill="black" if cell_info.colour != "black" else "white",
            align="center",
            font=ImageFont.truetype(self.base_font_path, self.font_size),
            spacing=2,
            anchor="mm"
        )

    def fill_cell_if_text(self, draw:ImageDraw, cell_info:ScoreboardCellInfoDto):
        if (cell_info.text is None) or (cell_info.text == ""):
            return
        draw.rectangle(
            xy=cell_info.get_rectangle_coords(self.get_cumulative_cell_widths()),
            fill=cell_info.colour
        )

    def build_cell_information(self, game_score) -> list[list[ScoreboardCellInfoDto]]:
        ## Don't consider logo here
        top_row = []
        bottom_row = []
        ## Player names
        server = game_score.get("next_server") or game_score.get("server")
        col_ix = 1
        top_row.append(
            ScoreboardCellInfoDto(
                text="\n".join(self.us_name),
                col_ix=col_ix,
                row_ix=0,
                height=self.cell_height,
                width=self.widths['player_names'],
                colour="green" if server == "us" else "white"
            )
        )
        bottom_row.append(
            ScoreboardCellInfoDto(
                text="\n".join(self.them_name),
                col_ix=col_ix,
                row_ix=1,
                height=self.cell_height,
                width=self.widths['player_names'],
                colour="green" if server != "us" else "white"
            )
        )
        col_ix += 1
        ## Set games
        for set_dict in self.sets_dicts:
            top_row.append(
                ScoreboardCellInfoDto(
                    text=set_dict['us'],
                    col_ix=col_ix,
                    row_ix=0,
                    height=self.cell_height,
                    width=self.widths['set_games'],
                    colour="black"
                )
            )
            bottom_row.append(
                ScoreboardCellInfoDto(
                    col_ix=col_ix,
                    row_ix=1,
                    text=set_dict['them'],
                    height=self.cell_height,
                    width=self.widths['set_games'],
                    colour="black"
                )
            )
            col_ix += 1
        ## Game score
        top_row.append(
            ScoreboardCellInfoDto(
                text=self.game_score['us'],
                col_ix=col_ix,
                row_ix=0,
                height=self.cell_height,
                width=self.widths['game_scores'],
                colour="white"
            )
        )
        bottom_row.append(
            ScoreboardCellInfoDto(
                text=self.game_score['them'],
                col_ix=col_ix,
                row_ix=1,
                height=self.cell_height,
                width=self.widths['game_scores'],
                colour="white"
            )
        )

        return [
            top_row,
            bottom_row
        ]

    def generate_scoreboard_image(
        self,
        sets_dicts: list,
        game_score: dict,
        set_ix=0,
        frame_ix=0,
        output_path2=None
    ):
        self.sets_dicts = sets_dicts
        self.game_score = game_score
        cols = 3 + len(sets_dicts)
        rows = 2

        # ---------- logo ----------
        logo_path = (
            Path(__file__)
            .resolve()
            .parents[2]      # go up to project root
            / "logos"
            / "PadelPointerWithTextV2.png"
        )
        logo_img = Image.open(logo_path).convert("RGBA")

        # scoreboard_width = cols * cell_width
        height = rows * self.cell_height

        # scale logo to fit height
        # scale = self.widths['logo'] / logo_img.width
        logo_img = logo_img.resize(
            (int(self.widths['logo']), int(self.widths['logo'])),
            Image.LANCZOS
        )
        width = self.calculate_scoreboard_width(self.widths)
        # scoreboard_width = width - self.widths['logo']

        # ---------- transparent base image ----------
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # paste logo
        img.paste(logo_img, (0, 0), logo_img)

        cell_informations = self.build_cell_information(game_score)
        cumulative_cell_widths = self.get_cumulative_cell_widths()
        cell_widths = self.get_cell_widths()

        for y in range(len(cell_informations)):
            for x in range(len(cell_informations[0])):
                cell_info = cell_informations[y][x]
                x0 = cell_info.get_x0(cumulative_cell_widths)
                y0 = cell_info.get_y0()
                width = cell_widths[cell_info.col_ix]
                self.fill_cell_if_text(draw, cell_info)
                self.draw_centered_text(draw, cell_info)
                if y == 1:
                    ## Draw vertical line
                    draw.line((x0, 0, x0, 2 * self.cell_height), fill="black", width=2)
        return img