import tkinter as tk
import numpy as np
import heapq
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape

#user defined
from cell import Cell

class UUVAgent(mesa.Agent):
    """UUV agent testing class"""

    def __init__(self, model, spawn, map, target, canvas, grid, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        # Target and spawn
        self.spawn = spawn
        self.dest = target
        self.position = [grid[spawn[0]][spawn[1]].pos_x, grid[spawn[0]][spawn[1]].pos_y]
        self.target = [grid[target[0]][target[1]].pos_x, grid[target[0]][target[1]].pos_y]

        # tkinter gui
        self.map = map
        self.canvas = canvas
        self.oval = self.canvas.create_oval(self.position[0]-5,self.position[1]-5, self.position[0]+5, self.position[1]+5, fill='blue', tags='agent')
        self.canvas.lift(self.oval)

        #varibles
        self.depth_preferd = [10, 20]
        self.depth_min = 5
<<<<<<< Updated upstream
        self.depth_max = 30
        # self.current_depth = self.map.depth_loc(x=self.position[0], y=self.position[1])
=======
>>>>>>> Stashed changes

        # Serch parameters
        self.grid = np.array(grid)
        self.ROW, self.COL = self.grid.shape
        self.grid = grid
        self.path = None
        self.a_star_search()
        tmp = self.path[0]
        self.next_target = self.grid[tmp[0]][tmp[1]]
<<<<<<< Updated upstream
        # print(self.next_target)
    
=======

>>>>>>> Stashed changes
    def getTargetDir(self):
        target_x = self.next_target.pos_x
        target_y = self.next_target.pos_y
        new_x = target_x - self.position[0]
        new_y = target_y - self.position[1]
        new_vector = np.array([new_x, new_y])
        magnitude = np.linalg.norm(new_vector)
        unit_vector =0

        if(magnitude == 0):
            if not self.path:
                unit_vector = [0, 0]
                return unit_vector
            else:
                self.path.pop(0)
                if not self.path or len(self.path) == 0:
                    return [0, 0]
                tmp = self.path[0]
                self.next_target = self.grid[tmp[0]][tmp[1]]
                unit_vector = [0, 0]
        else:
            unit_vector = new_vector / magnitude
        return unit_vector
        
    def move_to_target(self):
        """simple move towards target set function"""
        new_direction = self.getTargetDir()
        if (self.position[0] != self.target[0]) or (self.position[1] != self.target[1]):
            new_x = np.round(new_direction[0]).astype(int)
            new_y = np.round(new_direction[1]).astype(int)
            self.position = np.array([self.position[0] + new_x, self.position[1]+new_y])
            self.canvas.move(self.oval, new_x, new_y)     
            self.canvas.itemconfig(self.oval, fill="red")  # Change color to red while moving

    def a_star_search(self):
        """A* seach algorithum"""
        if not self.is_valid(self.spawn[0], self.spawn[1]) or not self.is_valid(self.dest[0], self.dest[1]):
            return

        if not self.is_unblocked(self.spawn[0], self.spawn[1]) or not self.is_unblocked(self.dest[0], self.dest[1]):
            return

        if self.is_destination(self.spawn[0], self.spawn[1]):
            return

        closed_list = [[False for _ in range(self.COL)] for _ in range(self.ROW)]
        cell_details = [[Cell(id=0) for _ in range(self.COL)] for _ in range(self.ROW)]

        i = self.spawn[0]
        j = self.spawn[1]
        cell_details[i][j].f = 0
        cell_details[i][j].g = 0
        cell_details[i][j].h = 0
        cell_details[i][j].parent_row_i = i
        cell_details[i][j].parent_col_j = j

        open_list = []
        heapq.heappush(open_list, (0.0, i, j))

        found_dest = False

        while len(open_list) > 0:
            p = heapq.heappop(open_list)
            i = p[1]
            j = p[2]
            closed_list[i][j] = True

            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dir in directions:
                new_i = i + dir[0]
                new_j = j + dir[1]

                if self.is_valid(new_i, new_j) and self.is_unblocked(new_i, new_j) and not closed_list[new_i][new_j]:
                    if self.is_destination(new_i, new_j):
                        cell_details[new_i][new_j].parent_row_i = i
                        cell_details[new_i][new_j].parent_col_j = j
                        self.trace_path(cell_details, self.dest)
                        found_dest = True
                        return
                    else:
                        g_new = cell_details[i][j].g + 1.0
                        h_new = self.calculate_h_value(new_i, new_j)
                        f_new = g_new + h_new

                        if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                            heapq.heappush(open_list, (f_new, new_i, new_j))
                            cell_details[new_i][new_j].f = f_new
                            cell_details[new_i][new_j].g = g_new
                            cell_details[new_i][new_j].h = h_new
                            cell_details[new_i][new_j].parent_row_i = i
                            cell_details[new_i][new_j].parent_col_j = j

        if not found_dest:
            pass

    def trace_path(self, cell_details, dest):
        path = []
        row = dest[0]
        col = dest[1]

        while not (cell_details[row][col].parent_row_i == row and cell_details[row][col].parent_col_j == col):
            path.append((row, col))
            temp_row = cell_details[row][col].parent_row_i
            temp_col = cell_details[row][col].parent_col_j
            row = temp_row
            col = temp_col

        path.append((row, col))
        path.reverse()
        self.path = path

    def is_valid(self, row, col):
        return (row >= 0) and (row < self.ROW) and (col >= 0) and (col < self.COL)

    def is_unblocked(self, row, col):
        return self.grid[row][col].id != 1

    def is_destination(self, row, col):
        return row == self.dest[0] and col == self.dest[1]

    def calculate_h_value(self, row, col):
        return ((row - self.dest[0]) ** 2 + (col - self.dest[1]) ** 2) ** 0.5