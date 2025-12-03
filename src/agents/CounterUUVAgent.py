# --- Project Information ---
# Project: UUV Simulation Framework
# Version: 1.0.0
# Date: November 2025
# 
# --- Authors and Contributors ---
# Primary:
# - Gunner Cook-Dumas (SCRUM Manager, Backend, Agent, Model, and GA Stucture)
# - Justin Mosman (developer)
# - Michael Cardinal (developer)
# 
# Secondary:
# - Lauren Milne (SCRUM Product Owner)
# 
# --- Reviewers/Bosses ---
# - Prof. Lance Fiondella, ECE, University of Massachusetts Dartmouth
# - Prof. Hang Dinh, CIS, Indiana University South Bend

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


from PIL import Image, ImageTk
import os
icon_path = os.path.join(os.getcwd(), "resources", "CUUV.png")

class CUUVAgent(mesa.Agent):
    DEFAULT_COLOR = "#028CFD"
    SPRITE_PATH = icon_path
    def __init__(self, model, spawn, grid, map, canvas, *args, **kwargs): 
        super().__init__(model)

        # Spawn and target
        self.spawn = spawn
        self.grid = np.array(grid)
        self.target = kwargs.get('target_agent', None)  # Get target from kwargs
        # Position and destination
        self.position = [grid[spawn[1]][spawn[0]].pos_x, grid[spawn[1]][spawn[0]].pos_y]
        

        # tkinter GUI
        self.color = kwargs.get('color', self.DEFAULT_COLOR)
        self.map = map
        self.canvas = canvas
        #self.oval = self.canvas.create_oval(
         #   self.position[0] - 5, self.position[1] - 5,
          #  self.position[0] + 5, self.position[1] + 5,
           # fill=self.color, tags='agent'
        #)
        #self.canvas.lift(self.oval)

        try:
            img = Image.open(icon_path)  
            img = img.resize((20, 20), Image.Resampling.LANCZOS)  # change size here
            self.icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print("Error loading target icon:", e)
            self.icon = None

        if self.icon is not None:
            self.sprite = self.canvas.create_image(
            self.position[0], 
            self.position[1], 
            image=self.icon,
            tags="agent"
        )
        else:
            # fallback: draw oval if icon fails
            self.sprite = self.canvas.create_oval(
            self.position[0]-5, self.position[1]-5,
            self.position[0]+5, self.position[1]+5,
            fill=self.color,
            tags="agent"
        )
        self.canvas.lift(self.sprite)

        # Movement parameters
        self.speed = 2  # Speed of movement per step

    def move_to_target(self):
        """
        Move the CounterUUV toward its target.
        Collision detection handled by model.check_collisions().
        """
        # Check if target exists and is valid
        if self.target is None or not hasattr(self.target, 'position'):
            return
        
        # Check if target is already neutralized
        if hasattr(self.target, 'status') and not self.target.status:
            self.target = None  # Clear target
            return
        
        self.dest = self.target.position  # Update where to go each step

        # Calculate the direction vector
        dx = self.dest[0] - self.position[0]
        dy = self.dest[1] - self.position[1]
        distance = (dx**2 + dy**2)**0.5

        # Avoid division by zero
        if distance == 0:
            return

        # Normalize the direction vector and scale by speed
        direction_x = (dx / distance) * self.speed
        direction_y = (dy / distance) * self.speed

        # Update the position
        self.position[0] += direction_x
        self.position[1] += direction_y

        # Update the canvas oval position
        self.canvas.move(self.sprite, direction_x, direction_y)

    def step(self):
        #print("DEBUG: CUUV Step, Position:", self.position)
        self.move_to_target()

    def cleanup(self):
        try:
            if hasattr(self, "sprite") and self.sprite is not None:
                try:
                    self.canvas.delete(self.sprite)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if hasattr(self, "radius_oval") and self.radius_oval is not None:
                try:
                    self.canvas.delete(self.radius_oval)
                except Exception:
                    pass
        except Exception:
            pass
        