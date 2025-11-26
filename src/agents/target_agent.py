# src/agents/target_agent.py
import mesa
import numpy as np

class TargetAgent(mesa.Agent):
    """Stationary or mobile target agent"""
    DEFAULT_COLOR = "#020EFD"
    def __init__(self, model, spawn, map, canvas, grid, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        
        # Position setup
        self.spawn = spawn
        self.grid = grid

        # Validate spawn coordinates
        if (spawn[1] < 0 or spawn[1] >= len(grid) or 
            spawn[0] < 0 or spawn[0] >= len(grid[0])):
            print(f"ERROR: Target spawn {spawn} is out of grid bounds!")
            print(f"Grid size: {len(grid)} rows x {len(grid[0]) if grid else 0} cols")
            # Use a safe fallback position (center of grid)
            safe_row = len(grid) // 2
            safe_col = len(grid[0]) // 2
            self.spawn = [safe_col, safe_row]
            spawn = self.spawn

        self.position = [
            grid[spawn[1]][spawn[0]].pos_x, 
            grid[spawn[1]][spawn[0]].pos_y
        ]
        
        #print(f"=== TARGET AGENT CREATED ===")
        #print(f"Target ID: {self.unique_id}")
        #print(f"Spawn grid coords: {spawn}")
        #print(f"Position (pixels): {self.position}")
        #print(f"=== END TARGET INIT ===\n")
        
        # Visual representation
        self.color = kwargs.get('color', self.DEFAULT_COLOR)
        self.canvas = canvas
        self.map = map
        self.oval = self.canvas.create_oval(
            self.position[0]-5, self.position[1]-5,
            self.position[0]+5, self.position[1]+5,
            fill=self.color, tags='target'
        )
        self.canvas.lift(self.oval)
        
        # Properties
        self.status = True #variable to see if target is destroyed or not
        
        
    def step(self):
        """Called each simulation tick"""
  
       
    
    def cleanup(self):
        """Remove canvas items"""
        try:
            if hasattr(self, "oval") and self.oval is not None:
                self.canvas.delete(self.oval)
        except Exception:
            pass