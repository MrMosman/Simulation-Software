import tkinter as tk
import numpy as np
import heapq
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape

#user defined
from cell import Cell

class SearchAgent(mesa.Agent):
    '''Search Agent for GA'''
    # keep in mind that the spawns pos(x,y) are flipped
    def __init__(self, model, spawn, map, canvas, grid, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        # Target and spawn
        
        self.spawn = spawn
        self.pos_pixel = [grid[spawn[1]][spawn[0]].pos_x, grid[spawn[1]][spawn[0]].pos_y] #[x,y] for canvas
        self.grid_index = [spawn[1], spawn[0]]
        self.grid = np.array(grid)
        self.ROW, self.COL = self.grid.shape
        self.grid = grid

        # Genetic Algo Vars
        self.chromosone = {
            'pos': [],   #final position
            'tot_moves': 0,         #how many times it moved
            'commands' : ['R', 'R', 'R'],        #list of movment commands
            'failed'   : False      #for if detected, died, crashed, etc
        }
        self.target = (17, 25) #remove hardcode latter for 
        self.fitness = 0
        self.is_failed = False
        self.next_command_num = 0



        # varibles
        self.radius = 20
        self.gui_color = 'red'
        self.tag = 'search'

        # tkinter gui
        self.map = map
        self.canvas = canvas
        self.oval = self.canvas.create_oval(self.pos_pixel[0]-5,self.pos_pixel[1]-5, self.pos_pixel[0]+5, self.pos_pixel[1]+5, fill=self.gui_color, tags=self.tag)
        self.canvas.lift(self.oval)
        

    def step(self):
        '''Called by the Mesa Model'''
        if not self.is_failed:
            if self.next_command_num < len(self.chromosone.get('commands')):
                next_command = self.chromosone.get('commands')[self.next_command_num]
                self.next_command_num +=1
                self.get_next_pos(next_command)
                self.update_icon_pos()
            else:
                return
            print(f'pix pos: {self.pos_pixel}')
            print(f'grid pos: {self.grid_index}')
            

    def get_next_pos(self, command):
        '''Return the next position and if valid'''
        match command:
            case 'L':
                if self.is_valid(self.grid_index[0]-1, self.grid_index[1]):# check if in bounds
                    if self.is_unblocked(self.grid_index[0]-1, self.grid_index[1]): # check if land
                        self.grid_index = [self.grid_index[0]-1, self.grid_index[1]]
                        self.pos_pixel = [self.grid[self.grid_index[0]][self.grid_index[1]].pos_x, self.grid[self.grid_index[0]][self.grid_index[1]].pos_y]
                        self.canvas.move(self.oval, self.pos_pixel[0], self.pos_pixel[1]) 
                    else:
                        print('hit land')
                        self.is_failed = True
                else:
                    print('out of bounds')
                    self.is_failed = True
            case 'R':
                if self.is_valid(self.grid_index[0]+1, self.grid_index[1]):# check if in bounds
                    if self.is_unblocked(self.grid_index[0]+1, self.grid_index[1]): # check if land
                        self.grid_index = [self.grid_index[0]+1, self.grid_index[1]]
                        self.pos_pixel = [self.grid[self.grid_index[0]][self.grid_index[1]].pos_x, self.grid[self.grid_index[0]][self.grid_index[1]].pos_y]
                        self.canvas.move(self.oval, self.pos_pixel[0], self.pos_pixel[1]) 
                    else:
                        print('hit land')
                        self.is_failed = True
                else:
                    print('out of bounds')
                    self.is_failed = True
            case 'U':
                if self.is_valid(self.grid_index[0], self.grid_index[1]-1):# check if in bounds
                    if self.is_unblocked(self.grid_index[0], self.grid_index[1]-1): # check if land
                        self.grid_index = [self.grid_index[0], self.grid_index[1]-1]
                        self.pos_pixel = [self.grid[self.grid_index[0]][self.grid_index[1]].pos_x, self.grid[self.grid_index[0]][self.grid_index[1]].pos_y]
                        self.canvas.move(self.oval, self.pos_pixel[0], self.pos_pixel[1]) 
                    else:
                        print('hit land')
                        self.is_failed = True
                else:
                    print('out of bounds')
                    self.is_failed = True
            case 'D':
                if self.is_valid(self.grid_index[0], self.grid_index[1]+1):# check if in bounds
                    if self.is_unblocked(self.grid_index[0], self.grid_index[1]+1): # check if 
                        self.grid_index = [self.grid_index[0], self.grid_index[1]+1]
                        self.pos_pixel = [self.grid[self.grid_index[0]][self.grid_index[1]].pos_x, self.grid[self.grid_index[0]][self.grid_index[1]].pos_y]

                        self.canvas.move(self.oval, self.pos_pixel[0], self.pos_pixel[1]) 
                    else:
                        print('hit land')
                        self.is_failed = True
                else:
                    print('out of bounds')
                    self.is_failed = True 
            case _:
                print(f"Unknow command : {command}")

    def is_valid(self, row, col):
        """Check if a cell is valid"""
        return (row >= 0) and (row < self.ROW) and (col >= 0) and (col < self.COL)

    def is_unblocked(self, row, col):
        """Check if cell is: 1 is land, 0 is water"""
        return self.grid[row][col].id != 1

    def is_destination(self, row, col):
        """Check if cell is the destination"""
        return row == self.dest[0] and col == self.dest[1]
    
    def update_icon_pos(self):
        '''update the coords of the icon on the canvas'''
        center_x = self.pos_pixel[0]
        center_y = self.pos_pixel[1]
        x1=center_x-5
        y1=center_y-5
        x2=center_x+5
        y2=center_y+5
        self.canvas.coords(self.oval, x1, y1, x2, y2) 




