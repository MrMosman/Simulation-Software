import tkinter as tk
import numpy as np
import pandas as pd
import mesa




from . import agent, detector_agent


class UUVModel(mesa.Model):
    """UUV model testing class"""

    AGENT_MAP = {
        "Seeker" : agent.UUVAgent,
        "Dector" : detector_agent.DetectorAgent
    }
    
    def __init__(self, n, spawns, map, targets, canvas, grid, *args, seed = None, rng = None, **kwargs):
        super().__init__(*args, seed=seed, rng=rng, **kwargs)
        # setup mesa controls

        # sim stuff gonna get changed
        self.num_agents = n
        self.canvas = canvas
        self.spawns = spawns
        self.targets = targets
        self.map = map


        # set agent populations
        self.population_count = {
            "Seeker": 0,
            "Detector": 0,
            "Targets" : 0
        }

        # position tracker
        self.population_position = {}

        # Grid stuff
        self.grid = grid
        #create agents
        for _ in range(self.num_agents):
            tmp_spwn = self.spawns[_]
            agent.UUVAgent.create_agents(model=self, n=1, target=self.targets, spawn=tmp_spwn, canvas=self.canvas, map=self.map, grid=self.grid)

    def step(self):
        """advance model by one step"""
        self.agents.do("move_to_target")

    def agent_registration(self, agent_instance, pos, type_name):
        '''Inital Agent registration'''
        # increase population for that agent type
        self.population_count[type_name] += 1
        self.population_position[pos].append(agent_instance)


    def create_agent(self, instruction):
        '''creates the agents in the model'''
        agent_type = instruction["type"]
        spawn_pos = instruction["pos"]
        
        AgentClass = self.AGENT_MAP.get(agent_type)

        if not AgentClass:
            print(f"Error: Unknown agent type {agent_type}")
            return

        # Prepare kwargs for the agent's constructor
        agent_kwargs = {
            "model": self, 
            "pos": spawn_pos,
            "canvas": self.canvas,
            "map": self.map, 
            "grid": self.grid,
            "type_name": agent_type # Pass the type name for easy identification
        }
        # Seeker agents need a 'target' parameter
        if agent_type == "Seeker":
             agent_kwargs["target"] = instruction.get("target", self.targets[0]) # Use a default target if not provided
        
        # Instantiate the agent
        new_agent = AgentClass(**agent_kwargs) 
        
        # Register the agent in the custom trackers and create it in the world 
        self.agent_registration(new_agent, spawn_pos, agent_type)
        AgentClass.create_agents(**agent_kwargs)




