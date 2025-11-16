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

#user defined
from cell import Cell

class DetectorAgent(mesa.Agent):
    '''Detector Agnet for a sensor'''
    # keep in mind that the spawns pos(x,y) are flipped
    def __init__(self, model, spawn, map, canvas, target, grid, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        # Target and spawn
        
        self.spawn = spawn
        self.position = [grid[spawn[1]][spawn[0]].pos_x, grid[spawn[1]][spawn[0]].pos_y]

        self.prob_log = [] #Holds the detection and probability data for plotting

        # varibles
        self.radius = 20

        # tkinter gui
        self.map = map
        self.canvas = canvas
        self.oval = self.canvas.create_oval(self.position[0]-5,self.position[1]-5, self.position[0]+5, self.position[1]+5, fill='white', tags='detector')
        self.radius_oval = self.canvas.create_oval(self.position[0]-self.radius, self.position[1]-self.radius, self.position[0]+self.radius, self.position[1]+self.radius, fill='', dash=(3,3) ,tags='detector')
        self.canvas.lift(self.oval)
        self.canvas.lift(self.radius_oval)

        self.Used = False

        plt.ion()               # plotting stuff
        self.fig, self.ax = plt.subplots()
        self.scatter = None

    def step(self):
        print("i have spawned")
        Detection = self.detect()
        self.update_plot()
        if not self.Used:
            print("Detection made by detector at position:", Detection.position)
            Detection = self.detect()
            if Detection:
                self.Used = True
                
                #Comment out to show the prob vs distance plot without spawning CUUVs
                #self.model.create_agent(type = "CUUV", pos = self.spawn, target = Detection)
            


    def detect(self):
        for agent in self.model.agents:
            if isinstance(agent, UUVAgent):
                dist = np.sqrt((self.position[0] - agent.position[0])**2 + (self.position[1] - agent.position[1])**2)
                if dist <= self.radius:
                    print("UUV is ", dist,  " units away from detector")

                    #IMPLEMENT DETECTION PROBABILITY
                    p = self.rayleigh(dist, sigma=10)

                    self.prob_log.append((dist, p)) #log distance and probability

                    if np.random.rand() < p:
                        print("Detected with probability:", p)
                        return agent
                    else:
                        print("Failed to detect (prob:", p, ")")

    

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

