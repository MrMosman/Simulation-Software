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
        self.position = [grid[spawn[1]][spawn[0]].pos_x, grid[spawn[1]][spawn[0]].pos_y]

        # Genetic Algo Vars
        self.chromosone = None
        self.target = (17, 25) #remove hardcode latter

        # varibles
        self.radius = 20
        self.gui_color = 'red'
        self.tag = 'search'

        # tkinter gui
        self.map = map
        self.canvas = canvas
        self.oval = self.canvas.create_oval(self.position[0]-5,self.position[1]-5, self.position[0]+5, self.position[1]+5, fill=self.gui_color, tags=self.tag)
        self.canvas.lift(self.oval)

    def step(self):
        print("i have spawned")