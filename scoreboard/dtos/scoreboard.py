from dataclasses import dataclass

@dataclass
class ScoreboardCellInfoDto:
    text: str|int
    col_ix: int
    row_ix: int
    height: int
    width: int
    colour: str
    is_transparent: bool

    def get_rectangle_coords(
        self,
        cumulative_cell_widths,
        cumulative_cell_heights
    ):
        ## x0,y0 is top left point
        x0 = self.get_x0(cumulative_cell_widths)
        y0 = self.get_y0(cumulative_cell_heights)
        ## x1,y1 is bottom right point
        x1 = x0 + self.width
        y1 = y0 + self.height
        return (x0,y0,x1,y1)
    
    def get_middle_of_cell(
        self,
        cumulative_cell_widths,
        cumulative_cell_heights
    ):
        x0 = self.get_x0(cumulative_cell_widths)
        y0 = self.get_y0(cumulative_cell_heights)
        return (x0 + 0.5*self.width, y0 + 0.5*self.height)
    
    def get_x0(
        self,
        cumulative_cell_widths
    ):
        return cumulative_cell_widths[self.col_ix - 1]
    
    def get_y0(self, cumulative_cell_heights):
        # return self.row_ix * self.height
        if self.row_ix == 0:
            return 0
        return cumulative_cell_heights[self.row_ix - 1]