import tkinter as tk
import numpy as np
import pandas as pd
import mesa 

from . import agent, detector_agent, search_agent, CounterUUVAgent, target_agent


class UUVModel(mesa.Model):
    """UUV model testing class"""
    # needs to be manually set here so spell correctly
    AGENT_MAP = {
        "seeker" : agent.UUVAgent,
        "detector" : detector_agent.DetectorAgent,
        "GA" : search_agent.SearchAgent,
        "CUUV" : CounterUUVAgent.CUUVAgent,
        "target" : target_agent.TargetAgent
    }
    # Universal agent types
    # if add new element must add a comma to end
    # ie ('target', 'test', ) <-see how there is a comma after the new 'test' agent
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
        #self.score_GA()



    def step(self):
        """advance model by one step"""
        self.agents.do("step")
        self.data_collector.collect(self)
        self.check_collisions()

        # retrive data from datacollecter
        raw_agent_data = self.data_collector.get_agent_vars_dataframe()
        #print("Model Stepping (Debugging)")
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
                self.score_GA()
                self.create_next_generation(agent_type="GA")
                # self.create_population()

>>>>>>>>> Temporary merge branch 2

    def agent_registration(self, agent_instance, pos, type_name):
        '''Inital Agent registration'''
        # increase population for that agent type
        self.population_count[type_name] += 1
        self.population_position[type_name].append(pos)

    def process_spawn_data(self, spawns):
            '''Process the raw spawn data from the gui'''
            #Debug
            #print(f"=== PROCESSING SPAWN DATA ===")
            #print(f"Spawn data categories: {list(spawns.keys())}")
            
            # iterate over outer dictionary
            for agent_category, spawn_list in spawns.items():
                print(f"\nCategory: {agent_category}, Count: {len(spawn_list)}")
                
                # iterate inside the dictionary
                for spawn_data in spawn_list:
                    agent_type = spawn_data.get('type')
                    agent_pos = spawn_data.get('pos')
                    agent_name = spawn_data.get('name')
                    
                    #print(f"  - Type: {agent_type}, Pos: {agent_pos}, Name: {agent_name}")
                    
                    self.agent_registration(agent_instance=agent_category, pos=agent_pos, type_name=agent_type)
            
            #print(f"\n=== END SPAWN DATA PROCESSING ===\n")
            #print(f"Population counts: {self.population_count}")
            #print(f"Population positions: {self.population_position}\n")

    def create_agent(self, type, pos, **parameters):
        '''creates the agents in the model'''
        agent_type = type
        spawn_pos = pos

        # Additional parameters
        extra_params = dict()
        if parameters:
            group_id = parameters.get("group_id", None)
            if group_id is not None:
                extra_params["group_id"]=group_id

            current_gen = parameters.get("gen", None)  # Fixed: added .get
            if current_gen is not None:
                extra_params["generation"] = current_gen

            chromosone = parameters.get("chromosone", None)  # Fixed: added .get
            if chromosone is not None:
                extra_params["chromosone"] = chromosone
            
            # Handle target_agent (for CUUV)
            target_agent = parameters.get("target_agent", None)
            if target_agent is not None:
                extra_params["target_agent"] = target_agent

        AgentClass = self.AGENT_MAP.get(agent_type)
        if not AgentClass:
            print(f"Error: Unknown agent type {agent_type}")
            return

        # Prepare kwargs for the agent's constructor      
        agent_kwargs = {
            "model": self,
            "spawn": spawn_pos,  # Fixed: was "n" : 1 which is wrong
            "map": self.map, 
            "canvas": self.canvas,
            "grid": self.grid
        }
        final_kwargs = {**agent_kwargs, **extra_params}

        # CREATE THE AGENT DIRECTLY (not via create_agents)
        agent_instance = AgentClass(**final_kwargs)
        return agent_instance
    
    def get_target_positions(self):
        """
        Return list of current target agent positions.
        Used by seeker agents to find targets dynamically.
        """
        #print("=== GET_TARGET_POSITIONS CALLED ===")
        
        target_class = self.AGENT_MAP.get("target")
        if not target_class:
            print("ERROR: No target class in AGENT_MAP")
            print(f"AGENT_MAP keys: {list(self.AGENT_MAP.keys())}")
            return []
        
        #print(f"Target class found: {target_class}")
        
        target_agents = self.agents_by_type.get(target_class, [])
        #print(f"Number of target agents: {len(target_agents)}")
        
        positions = []
        
        for agent in target_agents:
            #print(f"Checking target agent {agent.unique_id}:")
            #print(f"  - Has position: {hasattr(agent, 'position')}")
            #print(f"  - Position value: {getattr(agent, 'position', 'NO POSITION ATTR')}")
            #print(f"  - Has status: {hasattr(agent, 'status')}")
            #print(f"  - Status value: {getattr(agent, 'status', 'NO STATUS ATTR')}")
            
            # Check if status is True (alive)
            if hasattr(agent, 'position') and getattr(agent, 'status', True):
                positions.append(agent.position)
                #print(f"  -> ADDED to positions list")
            else:
                ...
                #print(f"  -> SKIPPED (dead or no position)")
        
        #print(f"Total positions returned: {len(positions)}")
        #print(f"Positions: {positions}")
        #print(f"=== END GET_TARGET_POSITIONS ===\n")
        
        return positions


    def check_collisions(self):
        """
        Check collisions for:
        1. Attackers reaching targets (sets target.status = False)
        2. CUUVs reaching attacker agents (sets attacker.status = False)
        """
        import numpy as np
        
        target_class = self.AGENT_MAP.get("target")
        cuuv_class = self.AGENT_MAP.get("CUUV")
        
        attacker_classes = [
            self.AGENT_MAP[t] for t in self.AGENT_CATEGORIES.get("attacker", [])
            if t in self.AGENT_MAP
        ]
        
        # 1. Check attacker -> target collisions
        if target_class:
            target_agents = list(self.agents_by_type.get(target_class, []))
            
            for target_agent in target_agents:
                # Skip if already destroyed
                if not getattr(target_agent, 'status', False):
                    continue
                    
                for attacker_agent in self.agents:
                    if type(attacker_agent) not in attacker_classes:
                        continue
                    
                    # Skip if attacker is dead
                    if not getattr(attacker_agent, 'status', False):
                        continue
                    
                    if not hasattr(attacker_agent, 'position') or not hasattr(target_agent, 'position'):
                        continue
                        
                    try:
                        dist = np.linalg.norm(
                            np.array(attacker_agent.position) - 
                            np.array(target_agent.position)
                        )
                        
                        if dist < 5:  # collision threshold (pixels)
                            print(f"Target {target_agent.unique_id} destroyed by attacker {attacker_agent.unique_id}!")
                            target_agent.status = False  # Mark as destroyed
                            #Update the target visuals to show death
                            try:
                                target_agent.canvas.itemconfig(target_agent.oval, fill='orange', outline='black', width=2)
                            except Exception:
                                pass
                             
                    except Exception as e:
                        print(f"Collision check error: {e}")
        
        # 2. Check CUUV -> attacker collisions
        if cuuv_class:
            cuuv_agents = list(self.agents_by_type.get(cuuv_class, []))
            
            for cuuv_agent in cuuv_agents:
                target_agent = getattr(cuuv_agent, 'target', None)
                
                if target_agent is None or not hasattr(target_agent, 'position'):
                    continue
                
                # Skip if target already dead
                if not getattr(target_agent, 'status', False):
                    cuuv_agent.target = None  # Clear CUUV's target
                    continue
                
                if not hasattr(cuuv_agent, 'position'):
                    continue
                
                try:
                    dist = np.linalg.norm(
                        np.array(cuuv_agent.position) - 
                        np.array(target_agent.position)
                    )
                    
                    if dist < 5:  # CUUV collision threshold (tighter)
                        print(f"CUUV {cuuv_agent.unique_id} neutralized attacker {target_agent.unique_id}!")
                        
                        # Kill the attacker
                        target_agent.status = False
                        
                        # Visual feedback for attacker
                        try:
                            target_agent.canvas.itemconfig(target_agent.oval, fill="#7C0000")
                        except Exception:
                            pass
                        
                        try:
                            cuuv_agent.canvas.itemconfig(cuuv_agent.oval, fill="#004075")
                        except Exception:
                            pass
                        
                        # Clear CUUV's target
                        cuuv_agent.target = None
                        
                except Exception as e:
                    print(f"CUUV collision check error: {e}")

                
    #def NI(self):
    #    """Next ID generator for agents"""
    #    self.NextID += 1
    #    return self.NextID 

    def create_GA_population(self, agent_type):
        """Create a random genome for a population"""
        return NotImplementedError
    
    def score_GA(self):
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
        my_lil_dude_list = list()
        tot_cost = 50*num_detector
        chosen_spawn=[]

        for _ in range(num_detector):
            sel_spawn = False
            while sel_spawn is False:
                spawn=self.random.choice(self.viable_spawns)
                if spawn not in chosen_spawn:
                    sel_spawn = True 

            lil_dude = self.create_agent(type="detector", pos=spawn)
            my_lil_dude_list.append(lil_dude)
        # get merge working
        individual = {"#_detc": num_detector, "agent_detc": my_lil_dude_list, "tot_cost": tot_cost}
        return individual



                fitness_score = agent.calculate_fitness()
                print(f"Agent ID: {agent.unique_id}, Fitness Score: {fitness_score}")
            
    def clear_agents(self):
        #This methods first gathers references to each agent, and calls the cleanup method on each agent. 
        #It then clears the model's agent container, grid backing, population trackers, and data collector.
        #This method is called within the reset simulation metheod in the GUI, some functionality is repeated but
        #this is to ensure that the model can be discarded cleanly without relying on the GUI to clean up everything.
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

        # 1) Clear agent container if present
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
            #Defensive check
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

        # 2) Clear grid backing
        try:
            if hasattr(self, "grid"):
                if hasattr(self.grid, "_grid"):
                    try:
                        self.grid._grid.clear()
                    except Exception:
                        pass
        except Exception:
            pass

        # 3) Reset population
        try:
            if hasattr(self, "population_count"):
                for k in list(self.population_count.keys()):
                    self.population_count[k] = 0
            if hasattr(self, "population_position"):
                for k in list(self.population_position.keys()):
                    self.population_position[k] = []
        except Exception:
            pass

        # 4) Clear data collector
        try:
            if hasattr(self, "data_collector"):
                self.data_collector = None
        except Exception:
            pass