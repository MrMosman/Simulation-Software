import tkinter as tk
import numpy as np
import pandas as pd
import mesa



from . import agent, detector_agent


class UUVModel(mesa.Model):
    """UUV model testing class"""
    
    def __init__(self, n, spawns, map, targets, canvas, grid, detector_spawn, detector_n,*args, seed = None, rng = None, **kwargs):
        super().__init__(*args, seed=seed, rng=rng, **kwargs)
        self.num_agents = n
        self.canvas = canvas
        self.spawns = spawns
        self.targets = targets
        self.map = map

        # Grid stuff
        self.grid = grid

        # testing new agent
        self.detector_n = detector_n
        self.detector_spawn = detector_spawn


        #create agents
        for _ in range(self.num_agents):
            tmp_spwn = self.spawns[_]
            agent.UUVAgent.create_agents(model=self, n=1, target=self.targets, spawn=tmp_spwn, canvas=self.canvas, map=self.map, grid=self.grid)

        print("is to make sensors")
        for _ in range(self.detector_n):
            tmp_spwn = self.detector_spawn[_]
            print(f'tmp spawn{tmp_spwn}')
            detector_agent.DetectorAgent.create_agents(model=self, n=1, spawns=tmp_spwn, canvas=self.canvas, map=self.map, grid=self.grid)

    def step(self):
        """advance model by one step"""
        self.agents.do("move_to_target")