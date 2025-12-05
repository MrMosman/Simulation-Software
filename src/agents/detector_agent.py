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
from .CounterUUVAgent import CUUVAgent
from .agent import UUVAgent
import matplotlib.pyplot as plt

from PIL import Image, ImageTk

import os
icon_path = os.path.join(os.getcwd(), "resources", "Detector.png")



#user defined
from cell import Cell

class DetectorAgent(mesa.Agent):
    '''Detector Agentt for a sensor'''
    DEFAULT_COLOR = "#FFFFFF"
    SPRITE_PATH = icon_path

    # keep in mind that the spawns pos(x,y) are flipped
    def __init__(self, model, spawn, map, canvas, grid, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        # Target and spawn
        
        self.spawn = spawn
        self.last_spawn_step = -999  # Track when we last spawned
        self.spawn_cooldown = 10  # Minimum steps between spawns
        self.position = [grid[spawn[1]][spawn[0]].pos_x, grid[spawn[1]][spawn[0]].pos_y]
        self.radius_color = kwargs.get('radius_color',self.DEFAULT_COLOR)
        self.prob_log = [] #Holds the detection and probability data for plotting

        # varibles
        self.radius = 20
        self.is_triggerd = False
    
        # tkinter gui
        self.color = kwargs.get('color', self.DEFAULT_COLOR)
        self.map = map
        self.canvas = canvas
        #self.oval = self.canvas.create_oval(
        #    self.position[0] - 5, self.position[1] - 5,
        #    self.position[0] + 5, self.position[1] + 5,
        #    fill=self.color, tags='agent'
        #)

        try:
            img = Image.open(icon_path)  
            img = img.resize((20, 20), Image.Resampling.LANCZOS)  # change size here
            self.icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print("Error loading agent icon:", e)
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

        self.radius_oval = self.canvas.create_oval(
            self.position[0] - self.radius, self.position[1] - self.radius,
            self.position[0] + self.radius, self.position[1] + self.radius,
            outline=self.radius_color, fill='', dash=(3, 3), tags='agent'
        )
        #self.canvas.lift(self.oval)
        self.canvas.lift(self.radius_oval)

        self.Used = False

        #plt.ion()               # plotting stuff
        # self.fig, self.ax = plt.subplots()
        self.scatter = None

    def step(self):
        if self.Used:
            return

        Detection = self.detect()
        
        current_step = self.model.schedule.steps if hasattr(self.model, 'schedule') else 0
        steps_since_spawn = current_step - self.last_spawn_step
        
        if Detection and not self.Used and steps_since_spawn >= self.spawn_cooldown:
            print(f"Detector {self.unique_id} detected agent {Detection.unique_id}!")
            self.Used = True
            self.last_spawn_step = current_step
            # Spawn CUUV at detector location targeting the detected agent
            self.model.create_agent(type="CUUV", pos=self.spawn, target_agent=Detection)
        
        # Update plot every step
        #self.update_plot()
                


    def detect(self):
        """Creates a pop up window"""
        for agent in self.model.agents:
            if isinstance(agent, UUVAgent):
                # Check if agent is still active
                if not getattr(agent, 'status', True):
                    continue
                    
                dist = np.sqrt((self.position[0] - agent.position[0])**2 + 
                            (self.position[1] - agent.position[1])**2)
                
                if dist <= self.radius:
                    print(f"UUV {agent.unique_id} is {dist:.2f} units away from detector")

                    # Calculate detection probability
                    p = self.rayleigh(dist, sigma=10)
                    self.prob_log.append((dist, p))

                    if np.random.rand() < p:
                        print(f"Detected with probability: {p:.3f}")
                        return agent
                    else:
                        print(f"Failed to detect (prob: {p:.3f})")
        
        return None  # Explicitly return None if no detection

    

    def rayleigh(self, distance, sigma=10):
        return np.exp(-(distance**2) / (2 * sigma**2))

    def update_plot(self):
        """Live-updates detection probability scatter plot."""
        if len(self.prob_log) == 0:
            return

        dist = [x[0] for x in self.prob_log]
        prob = [x[1] for x in self.prob_log]

        self.ax.clear()
        self.ax.scatter(dist, prob)
        self.ax.set_xlabel("Distance")
        self.ax.set_ylabel("Detection Probability")
        self.ax.set_title("Rayleigh Detection Probability vs Distance (Live)")

        self.ax.set_ylim(0, 1)
        self.ax.grid(True)

        plt.pause(0.001)

    def cleanup(self):
        """Remove this agent's canvas items (oval and detection radius)."""
        try:
            if hasattr(self, "oval") and self.oval is not None:
                try:
                    self.canvas.delete(self.oval)
                except Exception:
                    pass
        except Exception:
            pass
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
