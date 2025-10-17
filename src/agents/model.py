import tkinter as tk
import numpy as np
import pandas as pd
import mesa 



from . import agent, detector_agent, search_agent


class UUVModel(mesa.Model):
    """UUV model testing class"""

    # needs to be manulay set here so spell correctly
    AGENT_MAP = {
        "seeker" : agent.UUVAgent,
        "detector" : detector_agent.DetectorAgent,
        "GA" : search_agent.SearchAgent
    }

    # Univerisal agent types
    # if add new element must add a comma to end 
    # ie ('target', 'test', ) <-see how there is a comma after the new 'test' ageent
    AGENT_CATEGORIES = {
        "attacker" : ("seeker", "detector", "GA"),
        "defender" : ('target',)
    }

    # Genetic Algorithm parameters
    POP_SIZE = 10
    GENERATIONS = 50
    MUTATION_RATE = 0.1
    AGENT_CHROMESOME_COMMAND = {'L': 1, 'R': 2, 'U': 3, 'D': 4}
    
    def __init__(self, spawns, map, canvas, grid, *args, seed = None, rng = None, **kwargs):
        super().__init__(*args, seed=seed, rng=rng, **kwargs)
        # setup mesa controls

        # sim stuff gonna get changed
        # self.num_agents = n
        # self.targets = targets
        self.canvas = canvas
        self.spawns = spawns
        self.map = map
        self.grid = grid.grid

        # retrieve data types
        # flatten catagories
        self.all_agent_types = [
            agent_type
            for types_tuple in self.AGENT_CATEGORIES.values() # Get agent attatckers/defenders
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

        # Process the spawn data
        self.process_spawn_data(spawns=spawns)
        
        # #create agents
        for agent_type in self.all_agent_types:
            tmp_pos_list = self.population_position[agent_type]
            tmp_pop_count = self.population_count[agent_type]
            for i in range(tmp_pop_count):
                pos = tmp_pos_list[i]
                print(f'CREATE AGENT->type: {agent_type}, pos: {pos}')
                self.create_agent(type=agent_type, pos=pos)

        # Data cataloging
        self.data_collecter = mesa.DataCollector(
            agent_reporters={"Finnished_agent_count": "is_finnished"}
        )



    def step(self):
        """advance model by one step"""
        self.agents.do("step")
        self.data_collecter.collect(self)
        print(self.data_collecter.get_agent_vars_dataframe().head)

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
                # print(f'{agent_type} and {agent_pos}') #DEBUG
        # DEBUG 
        # print(self.population_count)
        # print(self.population_position)

    def create_agent(self, type, pos):
        '''creates the agents in the model'''
        # acces the instruciton keys
        agent_type = type
        spawn_pos = pos
        
        AgentClass = self.AGENT_MAP.get(agent_type)

        if not AgentClass:
            print(f"Error: Unknown agent type {agent_type}")
            return

        # Prepare kwargs for the agent's constructor self, model, spawn, map, canvas, grid,          
        agent_kwargs = {
            "model": self,
            "n" : 1,
            "spawn" : spawn_pos,
            "map" : self.map, 
            "canvas": self.canvas,
            "grid": self.grid
        }
        # # Seeker agents need a 'target' parameter
        # if agent_type == "Seeker":
        #      agent_kwargs["target"] = instruction.get("target", self.targets[0]) # Use a default target if not provided

        AgentClass.create_agents(**agent_kwargs)

    def create_GA_population(self, agent_type):
        """Create a random genome for a population"""
        return NotImplementedError


