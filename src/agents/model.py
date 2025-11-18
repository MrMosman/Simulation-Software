import tkinter as tk
import numpy as np
import pandas as pd
import mesa 



from . import agent, detector_agent, search_agent, CounterUUVAgent


class UUVModel(mesa.Model):
    """UUV model testing class"""

    # needs to be manulay set here so spell correctly
    AGENT_MAP = {
        "seeker" : agent.UUVAgent,
        "detector" : detector_agent.DetectorAgent,
        "GA" : search_agent.SearchAgent,
        "CUUV" : CounterUUVAgent.CUUVAgent
    }

    # Univerisal agent types
    # if add new element must add a comma to end 
    # ie ('target', 'test', ) <-see how there is a comma after the new 'test' ageent
    AGENT_CATEGORIES = {
        "attacker" : ("seeker", "GA"),
        "defender" : ('target',"detector", "CUUV",)
    }

    # Genetic Algorithm parameters
    POP_SIZE = 10
    GENERATIONS = 50
    MUTATION_RATE = 0.1
    AGENT_CHROMESOME_COMMAND = {'L': 1, 'R': 2, 'U': 3, 'D': 4}
    
    def __init__(self, spawns, map, canvas, grid, targets, *args, seed = None, rng = None, **kwargs):
        super().__init__(*args, seed=seed, rng=rng, **kwargs)
        # setup mesa controls

        # sim stuff gonna get changed
        # self.num_agents = n
        self.targets = targets
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
        
        #For agent ID implementation
        #self.NextID = 0

        # #create agents
        for agent_type in self.all_agent_types:
            tmp_pos_list = self.population_position[agent_type]
            tmp_pop_count = self.population_count[agent_type]
            if tmp_pop_count == 0:
                continue
            print(f"Current Agent is : {agent_type}")
            if agent_type == "GA":
                for i in range(tmp_pop_count):
                    pos = tmp_pos_list[i]
                    for _ in range(self.POP_SIZE):               
                        self.create_agent(type=agent_type, pos=pos, group_id=i)
                        print(f'CREATE AGENT->type: {agent_type}, pos: {pos}, group_id: {i}')
            else:
                for i in range(tmp_pop_count):
                    pos = tmp_pos_list[i]
                    print(f'CREATE AGENT->type: {agent_type}, pos: {pos}')
                    self.create_agent(type=agent_type, pos=pos, target=targets)

        # Data cataloging
        self.data_collector = mesa.DataCollector(
            agent_reporters={"Finnished_agent_count": "is_finnished",
            "position": "position",
            "Agent type": "Agent_ID"},
            model_reporters={"Step": lambda self: self.steps, "Total Agents": lambda self: len(self.agents)}
            
        
        )
        self.score_GA()



    def step(self):
        """advance model by one step"""
        self.agents.do("step")
        self.data_collector.collect(self)
        # print(self.data_collector.get_agent_vars_dataframe().head)
        print("Model Stepping (Debugging)")
        print(self.data_collector.get_model_vars_dataframe().head)
        self.score_GA()

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
                self.agent_registration(agent_instance=agent_category, pos=agent_pos, type_name=agent_type)
                print(f'{agent_type} and {agent_pos}') #DEBUG
        # DEBUG 
        # print(self.population_count)
        # print(self.population_position)

    def create_agent(self, type, pos, **parameters):
        '''creates the agents in the model'''
        # acces the instruciton keys
        agent_type = type
        spawn_pos = pos

        # Additional parameters
        extra_params = dict()
        if parameters:
            group_id = parameters.get("group_id", None)
            if group_id is not None:
                extra_params["group_id"]=parameters["group_id"]

            target = parameters.get("target", None)
        else:
            target = None
           
        
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
            "grid": self.grid,
            "target": target
            #"Agent ID": self.NI(),
            #"Agent_type": agent_type       
        }
        final_kwargs = {**agent_kwargs, **extra_params}

        AgentClass.create_agents(**final_kwargs)
        

    #def NI(self):
    #    """Next ID generator for agents"""
    #    self.NextID += 1
    #    return self.NextID 

    def create_GA_population(self, agent_type):
        """Create a random genome for a population"""
        return NotImplementedError
    
    def score_GA(self):
        """Scores and orders the fitness fucntion"""
        ga_class = self.AGENT_MAP.get('GA')
        ga_agent_set = self.agents_by_type.get(ga_class)
        if ga_agent_set:
            ga_population = list(ga_agent_set)
            ga_population = sorted(ga_population, key= lambda x:x.calculate_fitness())
            for agent in ga_population:
                # Call the method here as well to get the score
                fitness_score = agent.calculate_fitness()
                print(f"Agent ID: {agent.unique_id}, Fitness Score: {fitness_score}")
            
    def clear_agents(self):
        """Remove agents and clear model bookkeeping so the model can be discarded."""
        # 0) Defensive: try to iterate existing agents first and let them clean up
        try:
            agents_snapshot = []
            if hasattr(self, "agents"):
                # attempt to get an iterable snapshot of agents
                try:
                    agents_snapshot = list(self.agents)
                except Exception:
                    # fallback: some containers expose _agents dict
                    if hasattr(self.agents, "_agents"):
                        try:
                            agents_snapshot = list(self.agents._agents.values())
                        except Exception:
                            agents_snapshot = []
            # let agents perform their cleanup and remove their canvas items if present
            for a in agents_snapshot:
                try:
                    if hasattr(a, "cleanup"):
                        try:
                            a.cleanup()
                        except Exception:
                            pass
                    # remove agent's canvas oval if stored on the agent and model has a canvas
                    if hasattr(a, "oval") and hasattr(self, "canvas") and self.canvas is not None:
                        try:
                            self.canvas.delete(a.oval)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

        # 1) Clear scheduler/agent container if present
        try:
            if hasattr(self, "agents"):
                try:
                    self.agents.clear()
                except Exception:
                    # fallback for different AgentBuffer implementations
                    if hasattr(self.agents, "_agents"):
                        try:
                            self.agents._agents.clear()
                        except Exception:
                            pass
            if hasattr(self, "schedule"):
                try:
                    if hasattr(self.schedule, "_agents"):
                        self.schedule._agents.clear()
                    elif hasattr(self.schedule, "agents"):
                        self.schedule.agents.clear()
                except Exception:
                    pass
            # also clear any 'agents_by_type' mapping if present
            if hasattr(self, "agents_by_type"):
                try:
                    self.agents_by_type.clear()
                except Exception:
                    pass
        except Exception:
            print("Warning: could not fully clear schedule/agents container")

        # 2) Clear grid backing (if any)
        try:
            if hasattr(self, "grid"):
                if hasattr(self.grid, "_grid"):
                    try:
                        self.grid._grid.clear()
                    except Exception:
                        pass
        except Exception:
            pass

        # 3) Reset population bookkeeping
        try:
            if hasattr(self, "population_count"):
                for k in list(self.population_count.keys()):
                    self.population_count[k] = 0
            if hasattr(self, "population_position"):
                for k in list(self.population_position.keys()):
                    self.population_position[k] = []
        except Exception:
            pass

        # 4) Clear data collector (match attribute name used in __init__)
        try:
            # use the attribute name you actually assigned in __init__
            if hasattr(self, "data_collector"):
                self.data_collector = None
        except Exception:
            pass