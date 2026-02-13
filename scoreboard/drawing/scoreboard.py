from PIL import Image, ImageDraw, ImageFont
from ..dtos import ScoreboardCellInfoDto
from pathlib import Path
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP


class ScoreboardImageDrawer:

    def __init__(
        self,
        us_name,
        them_name,
        just_analysis=False
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

        self.multiplier = 1 if just_analysis else 10

        self.widths = {
            'logo' : 120 * self.multiplier,
            'player_names' : self.calculate_player_name_width(),
            'set_games' : 50 * self.multiplier,
            'game_scores' : 60 * self.multiplier,
        }
        self.scoreboard_cell_height = 60 * self.multiplier
        self.scoreboard_font_size = 20 * self.multiplier
        self.match_stats_font_size = 25 * self.multiplier
        
        self.stats_table_cell_height = 50 * self.multiplier
               
    def get_empty_opening_frame(self) -> Image:
        width = self.calculate_scoreboard_width()
        height = self.scoreboard_cell_height * 2
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))        
        return img

    def calculate_player_name_width(self):
        width = 0
        for name in [self.us_name, self.them_name]:
            width = self.get_width_from_str_or_list(name, width)
        return width
    
    def get_width_from_str_or_list(self, val, width):
        if isinstance(val, list):
            for nm in val:
                width = max(width, self.width_calc(nm))
        else:
            width = max(width, self.width_calc(val))
        return width

    def width_calc(self, name):
        return ((len(name)*20) + 5) * self.multiplier
    
    def calculate_scoreboard_width(self):
        return (
            self.widths['logo'] +
            (self.widths['set_games'] * 3) +
            self.widths['game_scores'] +
            self.widths['player_names']
        )
    
    def get_scoreboard_cell_widths(self):
        cell_widths = [
            self.widths['logo'],
            self.widths['player_names']
        ]
        for i in self.sets_dicts:
            cell_widths.append(self.widths['set_games'])
        cell_widths.append(self.widths['game_scores'])
        return cell_widths
    
    def get_cumulative_scoreboard_cell_widths(self):
        prev_val = 0
        cumulative_cell_widths = []
        for w in self.get_scoreboard_cell_widths():
            prev_val += w
            cumulative_cell_widths.append(prev_val)
        return cumulative_cell_widths

    def draw_centered_text(
            self,
            draw:ImageDraw,
            cell_info:ScoreboardCellInfoDto,
            font_size:int,
            cumulative_cell_widths:list,
            cumulative_cell_heights:list
        ):
        if (cell_info.text is None) or (cell_info.text == ""):
            return
        draw.multiline_text(
            xy=cell_info.get_middle_of_cell(cumulative_cell_widths, cumulative_cell_heights),
            text=str(cell_info.text),
            fill="black" if cell_info.colour != "black" else "white",
            align="center",
            font=ImageFont.truetype(self.base_font_path, font_size),
            spacing=2,
            anchor="mm"
        )

    def fill_cell_if_text(
        self,
        draw:ImageDraw,
        cell_info:ScoreboardCellInfoDto,
        cumulative_cell_widths:list,
        cumulative_cell_heights:list
    ):
        if (cell_info.text is None) or (cell_info.text == ""):
            return
        draw.rectangle(
            xy=cell_info.get_rectangle_coords(cumulative_cell_widths,cumulative_cell_heights),
            fill=cell_info.colour
        )

    def build_scoreboard_cell_information(self, game_score) -> list[list[ScoreboardCellInfoDto]]:
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
                height=self.scoreboard_cell_height,
                width=self.widths['player_names'],
                colour="green" if server == "us" else "white"
            )
        )
        bottom_row.append(
            ScoreboardCellInfoDto(
                text="\n".join(self.them_name),
                col_ix=col_ix,
                row_ix=1,
                height=self.scoreboard_cell_height,
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
                    height=self.scoreboard_cell_height,
                    width=self.widths['set_games'],
                    colour="black"
                )
            )
            bottom_row.append(
                ScoreboardCellInfoDto(
                    col_ix=col_ix,
                    row_ix=1,
                    text=set_dict['them'],
                    height=self.scoreboard_cell_height,
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
                height=self.scoreboard_cell_height,
                width=self.widths['game_scores'],
                colour="white"
            )
        )
        bottom_row.append(
            ScoreboardCellInfoDto(
                text=self.game_score['them'],
                col_ix=col_ix,
                row_ix=1,
                height=self.scoreboard_cell_height,
                width=self.widths['game_scores'],
                colour="white"
            )
        )

        return [
            top_row,
            bottom_row
        ]
    
    def generate_whole_screen_image(
        self,
        sets_dicts: list,
        game_score: dict,
        match_stats: dict            
    ):
        canvas_size = (1920, 1080)
        canvas_w, canvas_h = canvas_size

        # Create transparent base canvas
        canvas = Image.new("RGBA", canvas_size, (0,0,0,0))

        scoreboard_image = self.generate_scoreboard_image(
            sets_dicts,
            game_score,
        )
        target_h_a = int(canvas_h * 0.15)
        scale_a = target_h_a / scoreboard_image.height
        target_w_a = int(scoreboard_image.width * scale_a)

        scoreboard_image_resized = scoreboard_image.resize((target_w_a, target_h_a), Image.LANCZOS)
        canvas.paste(scoreboard_image_resized, (0, 0), scoreboard_image_resized)

        match_stats_table_image = self.generate_match_stats_table_image(match_stats)
        target_h_b = int(canvas_h * 0.75)
        scale_b = target_h_b / match_stats_table_image.height
        target_w_b = int(match_stats_table_image.width * scale_b)

        match_stats_table_image_resized = match_stats_table_image.resize((target_w_b, target_h_b), Image.LANCZOS)

        x_b = (canvas_w - target_w_b) // 2
        y_b = int(canvas_h * 0.20)

        canvas.paste(match_stats_table_image_resized, (x_b, y_b), match_stats_table_image_resized)

        return canvas
        

    def generate_match_stats_table_image(
        self,
        match_stats: dict
    ):
        metrics = OrderedDict(
            [
                ("Sets Won", "setsWon"),
                ("Games Won", "gamesWon"),
                ("Service Games\nWon", "serviceGamesWon"),
                ("Return Games\nWon", "returnGamesWon"),
                ("Points Won", "pointsWon"),
                ("Break Point\nConversion %", None),
                ("Deciding Points\nWon", "decidingPointsWon"),
            ]
        )
        column_widths = {
            v : self.widths['player_names']
            for v in [self.us_name, self.them_name]
        }
        row_heights = {}
        max_metric_width = 0
        for long_met in metrics.keys():
            met_list = long_met.split("\n")
            max_metric_width = self.get_width_from_str_or_list(met_list, max_metric_width)
            row_heights[long_met] = self.stats_table_cell_height \
                if len(met_list) == 1 else \
                self.stats_table_cell_height * 2
        column_widths[""] = max_metric_width

        table_width = sum(column_widths)
        table_height = sum(row_heights)
        margin_x = 6
        margin_y = 10
        width = table_width + (2 * margin_x * self.multiplier)
        height = table_height + (2 * margin_y * self.multiplier)

        transparency_percent = 20
        alpha = int(255 * (transparency_percent / 100))
        img = Image.new("RGBA", (width, height), (128, 128, 128, alpha)), 
        draw = ImageDraw.Draw(img)

        cell_informations = self.build_match_stats_table_cell(
            row_heights,
            column_widths,
            match_stats,
            metrics
        )
        cumulative_cell_widths = [
            margin_x + column_widths[self.us_name],
            margin_x + column_widths[self.us_name] + column_widths[""],
            margin_x + column_widths[self.us_name] + column_widths[""] + column_widths[self.them_name],
        ]
        cumulative_cell_heights = self.get_cumulative_match_stats_cell_heights(metrics, row_heights)
        for y in range(len(cell_informations)):
            for x in range(len(cell_informations[0])):
                cell_info = cell_informations[y][x]
                # x0 = cell_info.get_x0(cumulative_cell_widths)
                # y0 = cell_info.get_y0()
                # width = cell_widths[cell_info.col_ix]
                self.fill_cell_if_text(draw, cell_info)
                self.draw_centered_text(
                    draw,
                    cell_info,
                    self.match_stats_font_size,
                    cumulative_cell_widths,
                    cumulative_cell_heights
                )


    def get_cumulative_match_stats_cell_heights(self, metrics, row_heights, margin_y):
        val = margin_y
        listo = []
        for met in metrics.keys():
            val += row_heights[met]
            listo.append(val)
        return listo

    def build_match_stats_table_cell(
        self,
        row_heights:dict,
        column_widths:dict,
        match_stats:dict,
        metrics:OrderedDict
    ) -> list[list[ScoreboardCellInfoDto]]:
        rows = []
        ## Top row
        rows.append(
            [
                ScoreboardCellInfoDto(
                    text="\n".join(self.us_name),
                    col_ix=0,
                    row_ix=0,
                    height=row_heights[""],
                    width=column_widths[self.us_name],
                    is_transparent=True
                ),
                ScoreboardCellInfoDto(
                    text="",
                    col_ix=1,
                    row_ix=0,
                    height=row_heights[""],
                    width=column_widths[""],
                    is_transparent=True
                ),
                ScoreboardCellInfoDto(
                    text="\n".join(self.them_name),
                    col_ix=2,
                    row_ix=0,
                    height=row_heights[""],
                    width=column_widths[self.them_name],
                    is_transparent=True
                )
            ]
        )
        for ix, (long_met, short_met) in enumerate(metrics.items(), 1):
            rows.append(
                [
                    ScoreboardCellInfoDto(
                        text=self.get_match_stats_cell_value(short_met, self.us_name, match_stats),
                        col_ix=0,
                        row_ix=ix,
                        height=row_heights[long_met],
                        width=column_widths[self.us_name],
                        is_transparent=True
                    ),
                    ScoreboardCellInfoDto(
                        text=long_met,
                        col_ix=1,
                        row_ix=ix,
                        height=row_heights[long_met],
                        width=column_widths[""],
                        is_transparent=True
                    ),
                    ScoreboardCellInfoDto(
                        text=self.get_match_stats_cell_value(short_met, self.them_name, match_stats),
                        col_ix=2,
                        row_ix=ix,
                        height=row_heights[long_met],
                        width=column_widths[self.them_name],
                        is_transparent=True
                    )
                ]
            )
        return rows


    def get_match_stats_cell_value(self, short_met, pair_name, match_stats):
        if short_met is None:
            break_points = match_stats[pair_name]["breakPoints"]
            break_points_converted = match_stats[pair_name]["breakPointsConverted"]
            return f"{self.round_half_up(break_points / break_points_converted)}%"
        return match_stats[pair_name][short_met]
    

    def round_half_up(self, value, ndigits=0):
        exponent = Decimal('1').scaleb(-ndigits)
        return float(Decimal(str(value)).quantize(exponent, rounding=ROUND_HALF_UP))


    def generate_scoreboard_image(
        self,
        sets_dicts: list,
        game_score: dict,
    ):
        self.sets_dicts = sets_dicts
        self.game_score = game_score
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
        height = rows * self.scoreboard_cell_height
        logo_img = logo_img.resize(
            (int(self.widths['logo']), int(self.widths['logo'])),
            Image.LANCZOS
        )
        width = self.calculate_scoreboard_width()

        # ---------- transparent base image ----------
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # paste logo
        img.paste(logo_img, (0, 0), logo_img)

        cell_informations = self.build_scoreboard_cell_information(game_score)
        cumulative_cell_widths = self.get_cumulative_scoreboard_cell_widths()
        cell_widths = self.get_scoreboard_cell_widths()

        for y in range(len(cell_informations)):
            for x in range(len(cell_informations[0])):
                cell_info = cell_informations[y][x]
                x0 = cell_info.get_x0(cumulative_cell_widths)
                # y0 = cell_info.get_y0()
                # width = cell_widths[cell_info.col_ix]
                self.fill_cell_if_text(draw, cell_info)
                self.draw_centered_text(
                    draw=draw,
                    cell_info=cell_info,
                    font_size=self.scoreboard_font_size,
                    cumulative_cell_widths=cumulative_cell_widths
                )
                if y == 1:
                    ## Draw vertical line
                    draw.line((x0, 0, x0, 2 * self.scoreboard_cell_height), fill="black", width=2)
        return img