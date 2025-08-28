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
        # self.target = target
        print(f'spawn{spawn}')
        print(f'target{target}')

        self.position = [grid[spawn[0]][spawn[1]].pos_x, grid[spawn[0]][spawn[1]].pos_y]
        self.target = [grid[target[0]][target[1]].pos_x, grid[target[0]][target[1]].pos_y]
        print(f'pos={self.position}')
        print(f'tar={self.target}')

        # tkinter gui
        self.map = map
        self.canvas = canvas
        self.oval = self.canvas.create_oval(self.position[0]-5,self.position[1]-5, self.position[0]+5, self.position[1]+5, fill='orange', tags='agent')
        self.canvas.lift(self.oval)

        #varibles
        self.depth_min = 5
        self.current_depth = self.map.depth_loc(x=self.position[0], y=self.position[1])

        # Serch parameters
        self.grid = grid
        gx = round(self.position[0] / 13) * 13
        gy = round(self.position[1] / 13) * 13
        tx = round(self.target[0] / 13) * 13
        ty = round(self.target[1] / 13) * 13



    
    def getTargetDir(self):
        new_x = self.target[0] - self.position[0]
        new_y = self.target[1] - self.position[1]
        new_vector = np.array([new_x, new_y])
        magnitude = np.linalg.norm(new_vector)
        unit_vector =0

        #get the next depth
        current_depth = self.map.depth_loc(x=self.position[0], y=self.position[1])

        if(magnitude == 0):
            unit_vector = 0
        else:
            unit_vector = new_vector / magnitude
        return unit_vector
        
    def move_to_target(self):
        """simple move towards target set function"""
        new_direction = self.getTargetDir()
        if np.all(self.target != self.position):
            new_x = np.round(new_direction[0]).astype(int)
            new_y = np.round(new_direction[1]).astype(int)
            self.position = np.array([self.position[0] + new_x, self.position[1]+new_y])
            self.canvas.move(self.oval, new_x, new_y)     

    def a_star_search(self):
    #    check if start and target are valid
        # check if start and target are blocked
        # check if already at target

        # create visted cells
        closed_list = [[False for _ in range(self.COL)] for _ in range(self.ROW)]
        # create detailes of each cell and assume all land
        cell_details = [[Cell(id=1) for _ in range(self.COL)] for _ in range(self.ROW)]

        # start cell conditions
        i = self.src[0]
        j = self.src[1]
        cell_details[i][j].f = 0
        cell_details[i][j].g = 0
        cell_details[i][j].h = 0
        cell_details[i][j].parent_col_i = i
        cell_details[i][j].parent_row_i = j

        # make cells vistied list
        open_list = []
        heapq.heappush(open_list, (0.0, i, j))
        found_dest = False

        while len(open_list > 0):
            
            # pop cell with smallest f values
            p = heapq.heappop(open_list)

            # make cell as visted
            i = p[1]
            j = p[2]
            closed_list[i][j] = True

            # check succesoors in each directions
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

            for dir in directions:
                new_i = i + dir[0]
                new_j = j + dir[1]

                # if succesor is valid
                if ((new_i >= 0) and (new_i < self.ROW) and (new_j >= 0) and (new_j < self.COL) and ()):
                    pass
