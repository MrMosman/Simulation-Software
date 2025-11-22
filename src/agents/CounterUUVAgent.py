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

from salinity import Salinity
from temperature import Temperature

class CUUVAgent(mesa.Agent):
    def __init__(self, model, spawn, target, grid, map, canvas, *args, **kwargs): 
        super().__init__(model, *args, **kwargs)

        # Spawn and target
        self.spawn = spawn
        self.target = target
        self.grid = np.array(grid)

        # Position and destination
        self.position = [grid[spawn[1]][spawn[0]].pos_x, grid[spawn[1]][spawn[0]].pos_y]
        

        # tkinter GUI
        self.map = map
        self.canvas = canvas
        self.oval = self.canvas.create_oval(
            self.position[0] - 5, self.position[1] - 5,
            self.position[0] + 5, self.position[1] + 5,
            fill='blue', tags='agent'
        )
        self.canvas.lift(self.oval)

        # Movement parameters
        self.speed = 2  # Speed of movement per step

    def move_to_target(self):
        """
        Move the CounterUUV toward its target.
        """
        self.dest = self.target.position #Update where to go each step

        # Calculate the direction vector
        dx = self.dest[0] - self.position[0]
        dy = self.dest[1] - self.position[1]
        distance = (dx**2 + dy**2)**0.5

        # If the agent is close to the target, stop moving
        if distance < self.speed:
            print("CounterUUV reached the target.")
            self.target.status = False
            return

        # Normalize the direction vector and scale by speed
        direction_x = (dx / distance) * self.speed
        direction_y = (dy / distance) * self.speed

        # Update the position
        self.position[0] += direction_x
        self.position[1] += direction_y

        # Update the canvas oval position
        self.canvas.move(self.oval, direction_x, direction_y)

    def step(self):

        print("DEBUG: CUUV Step, Position:", self.position)
        self.move_to_target()