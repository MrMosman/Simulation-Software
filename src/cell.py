

import math
import heapq

class Cell:
    def __init__(self):
        # parrent row and col index
        self.parent_row_i = 0 
        self.parent_col_i = 0

        self.f = float('inf') # total cost of the cell
        self.g = float('inf') # cost from start to this cell
        self.h = 0  #guess value
        