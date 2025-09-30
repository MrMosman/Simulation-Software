import tkinter as tk
import numpy as np
import pandas as pd
import mesa




from . import agent, detector_agent


class UUVModel(mesa.Model):
    """UUV model testing class"""

    # needs to be manulay set here so spell correctly
    AGENT_MAP = {
        "seeker" : agent.UUVAgent,
        "detector" : detector_agent.DetectorAgent
    }

    # Univerisal agent types
    # if add new element must add a comma to end 
    # ie ('target', 'test', ) <-see how there is a comma after the new 'test' ageent
    AGENT_CATEGORIES = {
        "attacker" : ("seeker", "detector"),
        "defender" : ('target', 'gunner is cool')
    }
    
    def __init__(self, spawns, map, canvas, grid, *args, seed = None, rng = None, **kwargs):
        super().__init__(*args, seed=seed, rng=rng, **kwargs)
        # setup mesa controls

        # sim stuff gonna get changed
        # self.num_agents = n
        # self.targets = targets
        self.canvas = canvas
        self.spawns = spawns
        self.map = map
        self.grid = grid

        # flatten catagories
        self.all_agent_types = [
            agent_type
            for types_tuple in self.AGENT_CATEGORIES.values() # Get ('Seeker', 'Detector'), ('Target',)
            for agent_type in types_tuple                    # Flatten the tuples
        ]
        # set agent populations
        self.population_count = {
            agent_type : 0
            for agent_type in self.all_agent_types
        }
        # position tracker
        self.population_position = {
            agent_type : []
            for agent_type in self.all_agent_types
        }

        # Prcess the spawn data
        self.process_spawn_data(spawns=spawns)
        
        # #create agents
        # for _ in range(self.num_agents):
        #     tmp_spwn = self.spawns[_]
        #     agent.UUVAgent.create_agents(model=self, n=1, target=self.targets, spawn=tmp_spwn, canvas=self.canvas, map=self.map, grid=self.grid)

    def step(self):
        """advance model by one step"""
        self.agents.do("move_to_target")

    def agent_registration(self, agent_instance, pos, type_name):
        '''Inital Agent registration'''
        # increase population for that agent type
        self.population_count[type_name] += 1
        self.population_position[type_name].append(pos)

    def process_spawn_data(self, spawns):
        '''Process the raw spawn data from the gui'''
        # iterate over outer dictionary
        for agent_category, spawn_list in spawns.items():
            # iterate inside the dictionary
            for spawn_data in spawn_list:
                agent_type = spawn_data.get('type')
                agent_pos = spawn_data.get('pos')
                agent_name = spawn_data.get('name')
                self.agent_registration(agent_instance=agent_category, pos=agent_pos, type_name=agent_name)
                print(f'{agent_type} and {agent_pos}') #DEBUG
        # DEBUG 
        print(self.population_count)
        print(self.population_position)


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




