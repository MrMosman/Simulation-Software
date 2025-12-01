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

import mesa
import numpy as np

from PIL import Image, ImageTk
import os
icon_path = os.path.join(os.getcwd(), "resources", "Installation(Target).png")


class TargetAgent(mesa.Agent):
    """Stationary or mobile target agent"""
    DEFAULT_COLOR = "#020EFD"
    SPRITE_PATH = icon_path
    def __init__(self, model, spawn, map, canvas, grid, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        
        # Position setup
        self.spawn = spawn
        self.grid = grid

        # Validate spawn coordinates
        if (spawn[1] < 0 or spawn[1] >= len(grid) or 
            spawn[0] < 0 or spawn[0] >= len(grid[0])):
            print(f"ERROR: Target spawn {spawn} is out of grid bounds!")
            print(f"Grid size: {len(grid)} rows x {len(grid[0]) if grid else 0} cols")
            # Use a safe fallback position (center of grid)
            safe_row = len(grid) // 2
            safe_col = len(grid[0]) // 2
            self.spawn = [safe_col, safe_row]
            spawn = self.spawn

        self.position = [
            grid[spawn[1]][spawn[0]].pos_x, 
            grid[spawn[1]][spawn[0]].pos_y
        ]
        
        #print(f"=== TARGET AGENT CREATED ===")
        #print(f"Target ID: {self.unique_id}")
        #print(f"Spawn grid coords: {spawn}")
        #print(f"Position (pixels): {self.position}")
        #print(f"=== END TARGET INIT ===\n")
        
        # Visual representation
        self.color = kwargs.get('color', self.DEFAULT_COLOR)
        self.canvas = canvas
        self.map = map
        #self.oval = self.canvas.create_oval(
        #    self.position[0]-5, self.position[1]-5,
        #    self.position[0]+5, self.position[1]+5,
        #    fill=self.color, tags='target'
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
            tags="target"
        )
        else:
            # fallback: draw oval if icon fails
            self.sprite = self.canvas.create_oval(
            self.position[0]-5, self.position[1]-5,
            self.position[0]+5, self.position[1]+5,
            fill=self.color,
            tags="target"
        )
        self.canvas.lift(self.sprite)
        
        # Properties
        self.status = True #variable to see if target is destroyed or not
        
        
    def step(self):
        """Called each simulation tick"""
  
       
    
    def cleanup(self):
        """Remove canvas items"""
        try:
            if hasattr(self, "oval") and self.oval is not None:
                self.canvas.delete(self.sprite)
        except Exception:
            pass
        try:
            if hasattr(self, "sprite") and self.sprite is not None:
                self.canvas.delete(self.sprite)
        except Exception:
            pass