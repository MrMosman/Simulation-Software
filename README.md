# University of Massachusetts Dartmouth UUV SIM
### SCRUM 14 & 16 changelog:
Added Lines (New_Gui):
SCRUM 14:
144-152: Added function to add either target or seeker UUV name and spawn location, restoring previous functionality.
196-197: Call the above function within on_start_click
219-220: Reset the trackers to 0 within the reset_simulation when called

SCRUM 16 (New_gui):
72-77: Create scrollbar, listbox, and agent display data
83-85: Scrollbar and label pack
114-128: Added 2 functions, one to update agent listbox, other to add the agent to the listbox
218: Wipe the list upon resetting
417: Updates Listbox when agent is spawned

Changed lines in (Model_py):
SCRUM 16:
Needed to change line 85 from:
self.agent_registration(agent_instance=agent_category, pos=agent_pos, type_name=agent_name)

to:
self.agent_registration(agent_instance=agent_category, pos=agent_pos, type_name=agent_type)

reason: When trying to run the simulation I was getting an error because the type_name was being passed as the agents name, but the self.population_count takes the agent types so I changed it to agent_type. 


### 9/30/25
* Scrum merged the gd_gui to main
* implemented universal agent adding
* smoothed out some UI taking data from model
* reimplemented mnay of the old fuctions from the old gui

### 9/25/25
* moved more of the old Gui into the proper class
* figure out what controls what

### 9/24/25
* Updated a new gui script to handles classes
* cleaned up some code redundancies

### 9/3/25
* fixed the map to hanlde Multipolygon

### 8/27/25
* Added both the cell.py and grid.py for the A* algor
* reverted to older map_init as was mergeing islands
* succsefly place grid cell locations only on the map

### 8/26/25
* updated the map_init fucntion to merge and decrease polygons(too manny)

### 8/25/25
* Can spawn multiple agents with their targets
* added some UI for easier spawning
* update agent.py and model.py with better tracking and spawing
* included file selct for shapefile

### 8/22/25
* Set up the project to be more user friendly and include a README
* Added very basic agent that is viewable on the map
* map.py setup to control and build the maps from shapefiles and retrieve data
* model.py setup and controls the model of the simulation (just calls the agent to move for now)
* agent.py setup and controls the agent which only moves to a hard coded target
* Overall went ahead and organized, fixed issues, and comments
