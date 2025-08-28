import math
import heapq

class Cell:
    def __init__(self, id):
        # test if land(1) or water(0)
        self.id = id
        self.row = 0
        self.col = 0

        # parrent row and col index
        self.parent_row_i = 0 
        self.parent_col_i = 0

        # position
        self.pos_x = 0
        self.pos_y = 0
        self.f = float('inf') # total cost of the cell
        self.g = float('inf') # cost from start to this cell
        self.h = 0  #guess value

    def __str__(self):
        return f"{self.id}, {self.pos_x}x{self.pos_y}, C={self.col}, R={self.row}"
        