import tkinter as tk
import numpy as np
import heapq
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape

#user defined
from map import MapControl
from cell import Cell






class UUVAgent(mesa.Agent):
    """UUV agent testing class"""

    def __init__(self, model, spawn, map, target, canvas, grid, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        # Target and spawn
        self.spawn = spawn
        self.dest = target
        # print(f'spawn{spawn}')
        # print(f'target{target}')
        self.position = [grid[spawn[0]][spawn[1]].pos_x, grid[spawn[0]][spawn[1]].pos_y]
        self.target = [grid[target[0]][target[1]].pos_x, grid[target[0]][target[1]].pos_y]
        # print(f'pos={self.position}')
        # print(f'tar={self.target}')

        # tkinter gui
        self.map = map
        self.canvas = canvas
        self.oval = self.canvas.create_oval(self.position[0]-5,self.position[1]-5, self.position[0]+5, self.position[1]+5, fill='orange', tags='agent')
        self.canvas.lift(self.oval)

        #varibles
        self.depth_min = 5
        # self.current_depth = self.map.depth_loc(x=self.position[0], y=self.position[1])

        # Serch parameters
        self.grid = np.array(grid)
        self.ROW, self.COL = self.grid.shape
        self.grid = grid
        self.path = None
        # print(f'R={self.ROW}, C={self.COL}')
        self.a_star_search()
        # print(self.path[0])
        tmp = self.path[0]
        self.next_target = self.grid[tmp[0]][tmp[1]]
        print(self.next_target)
    
    def getTargetDir(self):
        target_x = self.next_target.pos_x
        target_y = self.next_target.pos_y
        # print(f'target: {target_x}x{target_y}')
        # print(f'pos:{self.position}')
        new_x = target_x - self.position[0]
        new_y = target_y - self.position[1]
        new_vector = np.array([new_x, new_y])
        magnitude = np.linalg.norm(new_vector)
        unit_vector =0

        #get the next depth
        # current_depth = self.map.depth_loc(x=self.position[0], y=self.position[1])

        # print(f'mag:{magnitude}')
        if(magnitude == 0):
            if not self.path:
                print("target is destroyed")
                unit_vector = [0, 0]
                return unit_vector
            else:
                self.path.pop(0)
                tmp = self.path[0]
                self.next_target = self.grid[tmp[0]][tmp[1]]
                print(f'next target: {self.next_target}')
                unit_vector = [0, 0]
        else:
            unit_vector = new_vector / magnitude
        print(f'unitvector{unit_vector}')
        return unit_vector
        
    def move_to_target(self):
        """simple move towards target set function"""
        new_direction = self.getTargetDir()
        print(f'{self.target}--{self.position}')
        print((self.position[1] != self.target[1]))
        print((self.position[0] != self.target[0]))
        if (self.position[0] != self.target[0]) or (self.position[1] != self.target[1]):
            new_x = np.round(new_direction[0]).astype(int)
            new_y = np.round(new_direction[1]).astype(int)
            print(f'new_x:{new_x}')
            print(f'new_y:{new_y}')
            self.position = np.array([self.position[0] + new_x, self.position[1]+new_y])
            self.canvas.move(self.oval, new_x, new_y)     

    def a_star_search(self):
        """A* seach algorithum"""
                # Check if the source and destination are valid
        if not self.is_valid(self.spawn[0], self.spawn[1]) or not self.is_valid(self.dest[0], self.dest[1]):
            print("Source or destination is invalid")
            return

        # Check if the source and destination are unblocked
        if not self.is_unblocked(self.spawn[0], self.spawn[1]) or not self.is_unblocked(self.dest[0], self.dest[1]):
            print("Source or the destination is blocked")
            return

        # Check if we are already at the destination
        if self.is_destination(self.spawn[0], self.spawn[1]):
            print("We are already at the destination")
            return

        # Initialize the closed list (visited cells)
        closed_list = [[False for _ in range(self.COL)] for _ in range(self.ROW)]
        # Initialize the details of each cell
        cell_details = [[Cell(id=0) for _ in range(self.COL)] for _ in range(self.ROW)]

        # Initialize the start cell details
        i = self.spawn[0]
        j = self.spawn[1]
        cell_details[i][j].f = 0
        cell_details[i][j].g = 0
        cell_details[i][j].h = 0
        cell_details[i][j].parent_row_i = i
        cell_details[i][j].parent_col_j = j

        # # Initialize the open list (cells to be visited) with the start cell
        open_list = []
        heapq.heappush(open_list, (0.0, i, j))

        # # Initialize the flag for whether destination is found
        found_dest = False

        # # Main loop of A* search algorithm
        while len(open_list) > 0:
            # Pop the cell with the smallest f value from the open list
            p = heapq.heappop(open_list)

            # Mark the cell as visited
            i = p[1]
            j = p[2]
            closed_list[i][j] = True

            # For each direction, check the successors
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dir in directions:
                new_i = i + dir[0]
                new_j = j + dir[1]

                # If the successor is valid, unblocked, and not visited
                if self.is_valid(new_i, new_j) and self.is_unblocked(new_i, new_j) and not closed_list[new_i][new_j]:
                    # If the successor is the destination
                    if self.is_destination(new_i, new_j):
                        # Set the parent of the destination cell
                        cell_details[new_i][new_j].parent_row_i = i
                        cell_details[new_i][new_j].parent_col_j = j
                        print("The destination cell is found")
                        # Trace and print the path from source to destination
                        self.trace_path(cell_details, self.dest)
                        found_dest = True
                        return
                    else:
                        # Calculate the new f, g, and h values
                        g_new = cell_details[i][j].g + 1.0
                        h_new = self.calculate_h_value(new_i, new_j)
                        f_new = g_new + h_new

                        # If the cell is not in the open list or the new f value is smaller
                        if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                            # Add the cell to the open list
                            heapq.heappush(open_list, (f_new, new_i, new_j))
                            # Update the cell details
                            cell_details[new_i][new_j].f = f_new
                            cell_details[new_i][new_j].g = g_new
                            cell_details[new_i][new_j].h = h_new
                            cell_details[new_i][new_j].parent_row_i = i
                            cell_details[new_i][new_j].parent_col_j = j

        # If the destination is not found after visiting all cells
        if not found_dest:
            print("Failed to find the destination cell")

    def trace_path(self, cell_details, dest):
        """traces the movement of the a*"""
        # print("The Path is ")
        path = []
        row = dest[0]
        col = dest[1]

        # Trace the path from destination to source using parent cells
        while not (cell_details[row][col].parent_row_i == row and cell_details[row][col].parent_col_j == col):
            path.append((row, col))
            temp_row = cell_details[row][col].parent_row_i
            temp_col = cell_details[row][col].parent_col_j
            row = temp_row
            col = temp_col

        # Add the source cell to the path
        path.append((row, col))
        # Reverse the path to get the path from source to destination
        path.reverse()
        self.path = path

        # Print the path
        for i in path:
            print("->", i, end=" ")
        print()

    def is_valid(self, row, col):
        """Check if a cell is valid"""
        return (row >= 0) and (row < self.ROW) and (col >= 0) and (col < self.COL)

    def is_unblocked(self, row, col):
        """check if cell is unblocked"""
        return self.grid[row][col].id != 1

    def is_destination(self, row, col):
        """check if cell si teh destination"""
        return row == self.dest[0] and col == self.dest[1]

    def calculate_h_value(self, row, col):
        """calculate the guess value of a cell, Euclidean"""
        return ((row - self.dest[0]) ** 2 + (col - self.dest[1]) ** 2) ** 0.5