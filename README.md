# University of Massachusetts Dartmouth UUV SIM

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
