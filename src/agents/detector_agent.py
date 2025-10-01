import tkinter as tk
import numpy as np
import heapq
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape

#user defined
from cell import Cell

class DetectorAgent(mesa.Agent):
    '''Detector Agnet for a sensor'''
    # keep in mind that the spawns pos(x,y) are flipped
    def __init__(self, model, spawn, map, canvas, grid, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        # Target and spawn
        
        self.spawn = spawn
        self.position = [grid[spawn[1]][spawn[0]].pos_x, grid[spawn[1]][spawn[0]].pos_y]


        # varibles
        self.radius = 20

        # tkinter gui
        self.map = map
        self.canvas = canvas
        self.oval = self.canvas.create_oval(self.position[0]-5,self.position[1]-5, self.position[0]+5, self.position[1]+5, fill='white', tags='detector')
        self.radius_oval = self.canvas.create_oval(self.position[0]-self.radius, self.position[1]-self.radius, self.position[0]+self.radius, self.position[1]+self.radius, fill='', dash=(3,3) ,tags='detector')
        self.canvas.lift(self.oval)
        self.canvas.lift(self.radius_oval)
        

    def move_to_target(self):
        print("i have spawned")
