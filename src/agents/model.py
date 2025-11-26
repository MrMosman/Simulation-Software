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
    
    def __init__(self, spawns, map, canvas, grid, targets, viable_spawn,*args, seed = None, rng = None, **kwargs):
        super().__init__(*args, seed=seed, rng=rng, **kwargs)
        # setup mesa controls

        # sim stuff gonna get changed
        # self.num_agents = n
        self.targets = targets
        self.canvas = canvas
        self.spawns = spawns
        self.map = map
        self.grid = grid.grid
        self.viable_spawns = viable_spawn

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
        self.save_list = list()

        # model GA assignments
        self.ga_model_active = True
        self.ga_model_pop = None
        if self.viable_spawns is not None:
            self.ga_model_pop = self.create_inital_model_pop(self.POP_SIZE)
        self.det_cost = 50

        # agent GA assignments
        self.current_generation = 0
        self.child_chromosones = list()
        self.create_initial_agent_pop()

        # Data cataloging
        self.data_collector = mesa.DataCollector(
            agent_reporters={"Finnished_agent_count": "is_finnished",
            "position": "position",
            "Agent type": "Agent_ID"},
            model_reporters={"Step": lambda self: self.steps, "Total Agents": lambda self: len(self.agents)}   
        )

    def step(self):
        """advance model by one step"""
        self.agents.do("step")
        self.data_collector.collect(self)

        # retrive data from datacollecter
        raw_agent_data = self.data_collector.get_agent_vars_dataframe()
        raw_model_data = self.data_collector.get_model_vars_dataframe()
        finished_count = 0
        if self.ga_model_active is False:
            if not raw_agent_data.empty and not raw_model_data.empty:
                # get agent data
                current_step = raw_agent_data.index.get_level_values('Step').max() # get the max of the Step
                is_finnsihed_step = raw_agent_data.xs(current_step, level="Step")['Finnished_agent_count'] # get the cross section of the newest step and Step
                finished_count = is_finnsihed_step.sum() #return a sum of how many agents have finnished
                print(f"Finished agents at step {current_step}: {finished_count}")
        
            if finished_count == len(self.agents):
                # add the losers to a kill list to remove later
                # self.remove_all_agents()
                # print(len(self.agents))
                self.current_generation+=1
                print(f"Current Generation: {self.current_generation}")
                self.score_ga_agents()
                self.create_next_generation(agent_type="GA")
                # self.create_population()

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
                extra_params["group_id"]=group_id

            current_gen = parameters.get("gen", None)
            if current_gen is not None:
                extra_params["generation"]=current_gen

            chromosone = parameters.get("chromosone", None)
            if chromosone is not None:
                extra_params["chromosone"]=chromosone

            # Temporary fix that dosnt work
            if agent_type == "seeker":
                target = parameters.get("target", None)
                if target is not None:
                    extra_params["target"]=target
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
        }
        final_kwargs = {**agent_kwargs, **extra_params}

        return AgentClass.create_agents(**final_kwargs)
    
    def score_ga_agents(self):
        """Scores and orders the fitness function"""
        ga_class = self.AGENT_MAP.get('GA')
        ga_agent_set = self.agents_by_type.get(ga_class)
        if ga_agent_set:
            ga_population = list(ga_agent_set)
            ga_population = sorted(ga_population, key= lambda x:x.calculate_fitness(), reverse=False)
            # DEBUG
            self.save_list = ga_population[:2] #get best
            for agent in ga_population[2:]:
                agent.kill_your_self_now()
                # Call the method here as well to get the score
                # print(f"Agent ID: {agent.unique_id}, Fitness Score: {agent.fitness}")
            
            # breed the parents
            child_chromosones = list()
            dad=self.save_list[0]
            mom=self.save_list[1]
            child_chromosones.append(dad.chromosone)
            child_chromosones.append(mom.chromosone)
            for _ in range(self.POP_SIZE-2): #subtract 2 for the parents
                child_chromosones.append(dad.mate(mom))
                # print(f"{_} child chromesone{dad.mate(mom)}")
            dad.kill_your_self_now()
            mom.kill_your_self_now()
            self.save_list.clear()
            self.child_chromosones=child_chromosones
            
    def create_initial_agent_pop(self):
         """Create the intial populations for the model use only once"""
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
                        self.create_agent(type=agent_type, pos=pos, group_id=i, gen=self.current_generation, chromosone=0)
                        print(f'CREATE AGENT->type: {agent_type}, pos: {pos}, group_id: {i}')            
            else:
                for i in range(tmp_pop_count):
                    pos = tmp_pos_list[i]
                    print(f'CREATE AGENT->type: {agent_type}, pos: {pos}')
                    self.create_agent(type=agent_type, pos=pos, target=self.targets)

    def create_next_generation(self, agent_type):     
        """Creates the next generation of for the GA agents, not the model"""
        tmp_pos_list = self.population_position[agent_type]
        tmp_pop_count = self.population_count[agent_type]
        for i in range(tmp_pop_count):
            pos = tmp_pos_list[i]
            for _ in range(self.POP_SIZE):               
                self.create_agent(type=agent_type, pos=pos, group_id=i, gen=self.current_generation, chromosone=self.child_chromosones[_])
                print(f'CREATE AGENT->type: {agent_type}, pos: {pos}, group_id: {i}')  

    def create_inital_model_pop(self, pop_size):
        """Creates the inital model ga population, not the same as create_intital_agent_pop"""
        population=[]
        for _ in range(pop_size):                      
            individual = self.create_model_agent()         
            print(individual)
            population.append(individual)
        return population
    
    def create_model_agent(self):
        """Creates the model GA agents"""
        num_detector = self.random.randrange(1, 3)
        detector_list = list()
        tot_cost = 50*num_detector
        chosen_spawn=[]

        for _ in range(num_detector):
            sel_spawn = False
            while sel_spawn is False:
                spawn=self.random.choice(self.viable_spawns)
                if spawn not in chosen_spawn:
                    sel_spawn = True 

            lil_dude = self.create_agent(type="detector", pos=spawn)
            detector_list.append(lil_dude)
        # get merge working
        individual = {"#_detc": num_detector, "agent_det": detector_list, "tot_cost": tot_cost}
        return individual

    def score_ga_model(self):
        """Scores the GA for the model agents, do not use for GA agents"""


