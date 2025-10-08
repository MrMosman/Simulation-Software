import tkinter as tk
from tkinter import filedialog as fd
import os
from PIL import Image
from PIL import ImageTk 
from grid import Grid
from map import MapControl
from agents import model

class App(tk.Tk):
    def __init__(self, title, size, parent_dir):
        # main setup
        super().__init__()
        self.app_height = size[1]
        self.app_width = size[0]
        self.title(title)
        self.geometry(f'{self.app_width}x{self.app_height}')
        self.resizable(False, False)

        # varibles
        self.map_file_path = None
        self.map_grid = None
        self.map_shallow_color = (170, 201, 250)
        self.map_deep_color = (0, 0, 26)
        self.canvas_size = (700, 700)
        self.is_running = False
        self.animation_job = None
        self.can_spawn = False

        # Handle spawn position data
        # dont change this unless you tell me
        # or have good reason
        self.all_agent_types = [
            agent_type
            for types_tuple in model.UUVModel.AGENT_CATEGORIES.values()
            for agent_type in types_tuple                    
        ]
        self.spawn_data = {
            agent_type : []
            for agent_type in self.all_agent_types
        }

        # Agent model
        self.mesa_model = None

        # logo
        self.logo_path = os.path.join(parent_dir, "resources", "umass_logo.ico")
        self.logo_image = Image.open(self.logo_path)
        self.logo_icon = ImageTk.PhotoImage(self.logo_image)
        self.iconphoto(False, self.logo_icon)

        # menus
        self.menu = Menu(parent=self, size=(300, self.app_height),color='white')
        self.file_menu = FileMenu(self, (self.app_width, 100), color='white')
        self.canvas_frame = CanvasFrame(self, self.canvas_size)
        self.popup_window = None

        # sub-menus
        self.file_section = GeneralFrames(parent=self.menu, size=(440, 90), side='top', text='Map Selction')
        self.agent_menu_section = GeneralFrames(parent=self.menu, size=(440, 200), side='top', text='Agent Selection')
        self.sim_options_section = GeneralFrames(parent=self.menu, size=(440, 150), side='top', text='Simulation Options')
        self.sub_sim_section = tk.Frame(self.sim_options_section)
        self.sub_sim_section.pack(expand=True)
        self.config_menu_section = GeneralFrames(parent=self.menu,size=(440,90),side='top',text="Config Options")
        self.sub_config_section = tk.Frame(self.config_menu_section)
        self.sub_config_section.pack(expand=True)
        

        #sub-menu buttons
        self.file_button = tk.Button(self.file_section, text="Select", command=self.select_file, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.agent_menu_button = tk.Button(self.agent_menu_section, text="Add Agent", command=self.create_popup, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        name_width = 10
        type_width = 8
        count_width = 4
        label_text = f"{'Name:':<{name_width}} {'Type:':<{type_width}} {'Count:':>{count_width}}"
        self.scrollbar_label = tk.Label(self.agent_menu_section, text=label_text, font=("Consolas", 12))
        self.scrollbar = tk.Scrollbar(self.agent_menu_section)
        self.agent_display_data = {}  # {(name, type): count}
        self.agent_listbox = tk.Listbox(self.agent_menu_section, font=("Consolas", 11), width=30, height=8)
        self.scrollbar.config(command=self.agent_listbox.yview)
        self.agent_listbox.config(yscrollcommand=self.scrollbar.set)
        self.start_button = tk.Button(self.sub_sim_section, text="▶ Start", command=self.on_start_click, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.reset_sim_button = tk.Button(self.sub_sim_section, text="Reset", command= lambda: self.reset_simulation(), bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.exit_sim_button = tk.Button(self.sub_sim_section, text="Exit", command=self.destroy, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.file_button.pack(side='top', pady=4)
        self.agent_menu_button.pack(side='top')
        self.scrollbar_label.pack(side='top', fill='y', anchor='nw', padx=(5,0), pady=(5,0))
        self.agent_listbox.pack(side='left', fill='y', padx=(0, 2))
        self.scrollbar.pack(side='right', fill='y')
        self.start_button.grid(row=0, column=0, padx=10, pady=5)
        self.reset_sim_button.grid(row=0, column=1, padx=10, pady=5)
        self.exit_sim_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.save_button = tk.Button(self.sub_config_section, text="Save Config", bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised", command=lambda: print("Save config - WIP"))
        self.load_button = tk.Button(self.sub_config_section, text="Load Config", bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised", command=lambda: print("Load config - WIP"))
        self.save_button.grid(row=0, column=0, padx=10, pady=5)
        self.load_button.grid(row=0, column=1, padx=10, pady=5)

        # labels in menus
        self.uuv_info_label = tk.Label(self.file_menu, text="Seekers: 0", font=("Arial", 11), anchor="w", justify="left")
        self.uuv_info_label.pack(fill="x", padx=10, pady=2)
        
        self.target_info_label = tk.Label(self.file_menu, text="Targets: 0", font=("Arial", 11), anchor="w", justify="left")
        self.target_info_label.pack(fill="x", padx=10, pady=2)

        self.coord_label = tk.Label(self.file_menu, text="Grid Position: (x, y) | [lat, lon]", font=("Arial", 11), anchor="w")
        self.coord_label.pack(fill="x", padx=10, pady=2)


        # canvas settings
        self.canvas = CanvasMap(self.canvas_frame, (700,700))

        # control bindings
        self.canvas.bind("<Motion>", self.update_hover_info)

        # run
        self.mainloop()

    def update_agent_info_label(self, agent_type, label_widget):
        """
        Updates the given label_widget with the count and positions of the specified agent_type.
        """
        agents = self.spawn_data.get(agent_type, [])
        count = len(agents)
        if count == 0:
            label_widget.config(text=f"{agent_type.title()}s: 0")
            return
        info_items = [f"{agent_type.title()}s: {count}"]
        for idx, agent in enumerate(agents, 1):
            info_items.append(f"#{idx}: {agent['pos']}")
        label_widget.config(text=" | ".join(info_items))

    def update_agent_listbox(self):
        """Refresh the agent Listbox with current agent data."""
        self.agent_listbox.delete(0, tk.END)
        # Set fixed widths for each column
        name_width = 12
        type_width = 10
        count_width = 4
        for (name, agent_type), count in self.agent_display_data.items():
            # Format each entry with fixed width columns
            entry = f"{name:<{name_width}} {agent_type:<{type_width}} {count:>{count_width}}"
            self.agent_listbox.insert(tk.END, entry)

    def add_agent_to_display(self, name, agent_type):
        """Add or update agent in the display dictionary."""
        key = (name, agent_type)
        if key in self.agent_display_data:
            self.agent_display_data[key] += 1
        else:
            self.agent_display_data[key] = 1
        self.update_agent_listbox()

    def select_file(self):
        '''command for map file selection'''
        self.map_file_path = fd.askopenfilename(title="Selct a shapfile",
                                   initialdir="/", 
                                   filetypes=[("Shape files", "*.shp")]
                                    )
        if self.map_file_path:
            print(f"Selcted file: {self.map_file_path}")
            self.create_map()
        else:
            print("no file selected")

    def create_map(self):
        '''command for map/grid creation'''
        self.current_map = MapControl(
            shape_path=self.map_file_path,
            canvas=self.canvas,
            shallow_color=self.map_shallow_color,
            deep_color=self.map_deep_color
        )
        self.map_grid = Grid(width=self.canvas_size[0], height=self.canvas_size[1], cells_n=50, canvas=self.canvas)
        self.canvas.config(background="#0A7005")
        self.canvas.unbind("<Button-1>")

    def on_start_click(self):
        '''Start the simulation and create the mesa_model'''
        self.can_spawn = False
        if self.is_running is False:
            self.canvas.unbind("<Button-1>")
            self.start_button.config(state="normal", bg="#333333", text="⏸ Running...", fg="white", command=self.on_start_click) 
            if self.mesa_model is None:
                if self.map_grid is None:
                    tk.messagebox.showerror("Error", "Please load a map before starting the simulation.")
                    self.start_button.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=self.on_start_click)
                    return
                # addationl parameters here
                # create the mesa_model here
                self.mesa_model = model.UUVModel(
                    spawns=self.spawn_data, 
                    map=self.current_map, 
                    grid=self.map_grid,
                    canvas=self.canvas
                    )
            self.update_agent_info_label('seeker', self.uuv_info_label)
            self.update_agent_info_label('target', self.target_info_label)
            self.is_running = True
            self.animate()
        else:
            if self.animation_job:
                self.after_cancel(self.animation_job)
                self.animation_job = None
            self.start_button.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=self.on_start_click)
            self.canvas_frame.config(bg="#333333")
            self.is_running = False
    
    def reset_simulation(self):
        '''WORK IN PROGRESS'''
        for item in self.canvas.find_all():
            tags = self.canvas.gettags(item)
            if "agent" in tags or "target" in tags or self.canvas.itemcget(item, "fill") in ["orange", "blue"]:
                self.canvas.delete(item)
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        self.is_running = False
        self.agent_listbox.delete(0, tk.END)
        self.uuv_info_label.config(text="Seekers: 0")
        self.target_info_label.config(text="Targets: 0")
        self.coord_label.config(text="Grid Position: (x, y) | [lat, lon]")
        self.start_button.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=self.on_start_click)
        self.canvas_frame.config(bg="#333333")

    def animate(self):
        '''animate the screen'''
        if self.is_running and self.mesa_model is not None:
            self.animation_job = self.after(50, self.animate)
            # step through the model
        else:
            self.animation_job = None

    def create_popup(self):
        '''create the popup window'''
        if self.popup_window is None:
            self.popup_window = UAVSelectWindow(self,"Select UAV", (400,300), self.canvas)

    def snap_to_grid(self, x, y):
        '''Snaps the mouse to the grid'''
        if self.map_grid is not None:
            grid_size = self.map_grid.cell_size
            snapped_x = round(x / grid_size) * grid_size
            snapped_y = round(y / grid_size) * grid_size
            grid_x = int(round(snapped_x / grid_size))
            grid_y = int(round(snapped_y / grid_size))
        else:
            snapped_x, snapped_y = x, y
            grid_x, grid_y = int(x), int(y)
        return snapped_x, snapped_y, grid_x, grid_y

    def is_inside_map(self, x, y):
        '''checks if inside the canvas bounds'''
        overlapping_items = self.canvas.find_overlapping(x, y, x, y)
        for item_id in overlapping_items:
            tags = self.canvas.gettags(item_id)
            if "map" in tags:
                return True
        return False

    def update_hover_info(self, event):
        '''updates the hover info and shows the current selected grid'''
        if self.map_grid is None:
            return
        grid_size = self.map_grid.cell_size
        snapped_x = round(event.x / grid_size)
        snapped_y = round(event.y / grid_size)
        if self.current_map is not None and hasattr(self.current_map, "canvas_to_latlon"):
            lat, lon = self.current_map.canvas_to_latlon(snapped_y * grid_size, snapped_x * grid_size)
            self.coord_label.config(text=f"Grid Position: ({snapped_x}, {snapped_y}) | [{lat:.3f}, {lon:.3f}]")
        else:
            self.coord_label.config(text="Grid Position: (x, y) | [lat, lon]")
        self.canvas.delete("hover_rect")
        x1 = snapped_x * grid_size - grid_size / 2
        y1 = snapped_y * grid_size - grid_size / 2
        x2 = x1 + grid_size
        y2 = y1 + grid_size
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=2, tags="hover_rect")


class Menu(tk.Frame):
    """Handles the menu for the UAV Agents"""
    def __init__(self, parent, size, color):
        super().__init__(parent, width=size[0], height=size[1], bg=color, border=5)
        self.padding = 5
        self.pack(side='right', padx=self.padding, pady=self.padding)
        self.pack_propagate(False)

class FileMenu(tk.Frame):
    '''Handles the file menu and output'''
    def __init__(self, parent, size, color):
        super().__init__(parent, width=size[0], height=size[1], bg=color, relief='flat')
        self.padding = 5
        self.pack(side='bottom', padx=self.padding, pady=self.padding)
        self.pack_propagate(False)

class CanvasFrame(tk.Frame):
    '''controls the frame canvas that the simulation runs in'''
    def __init__(self, parent, size):
        super().__init__(parent, background='#333333', width=size[0], height=size[1], relief="raised", border=5)
        self.padding = 5
        self.width = size[0]
        self.height = size[1]
        self.pack(side='left', padx=self.padding, pady=self.padding)
        self.pack_propagate(False)

class CanvasMap(tk.Canvas):
    '''Handles the physcal canvas to draw on for simulation'''
    def __init__(self, parent, size):
        super().__init__(background="#040404", master=parent, width=size[0], height=size[1])
        self.pack()
        self.pack_propagate(False)

class GeneralFrames(tk.Frame):
    '''general frames in the menus'''
    def __init__(self, parent, size, color=None, side=None, anchor=None, text=None):
        super().__init__(parent, width=size[0], height=size[1], bg=color, border=5, bd=2, relief='solid')
        self.padding = 5
        self.pack(side=side, padx=self.padding, pady=self.padding)
        self.pack_propagate(False) 
        if text != None:
            self.title = tk.Label(self, text=text, font=("Arial", 13, "bold"))
            self.title.pack(side='top', pady=(0, 2))
            self.file_bar = tk.Frame(self, bg="black", height=2)
            self.file_bar.pack(side="top", fill="x", pady=(0, 8))

class UAVSelectWindow(tk.Toplevel):
    '''UAV selecting popup window'''
    def __init__(self, parent, title, size, canvas):
        super().__init__(parent)
        # setup the window 
        self.parent = parent
        self.title=title
        self.geometry(f'{size[0]}x{size[1]}')
        self.attributes('-topmost', True)
        self.resizable(False, False)
        self.canvas = canvas
        self.protocol("WM_DELETE_WINDOW", self.close_popup)

        # gather agent data
        # dont change this unless you tell me
        # or have good reason
        self.agent_type_attacker = model.UUVModel.AGENT_CATEGORIES['attacker']
        self.agent_type_defender = model.UUVModel.AGENT_CATEGORIES['defender']

        # Setup button controles
        self.mode_var = tk.StringVar(self)
        self.mode_var.set("Attacker")
        self.name_label = tk.Label(self, text="Name:", font=("Arial", 11))
        self.name_label.pack(anchor="w", padx=20, pady=(20, 2))
        self.name_entry = tk.Entry(self, font=("Arial", 11), width=25)
        self.name_entry.pack(anchor="w", padx=20, pady=(0, 10))
        self.type_label = tk.Label(self, text="Type:", font=("Arial", 11))
        self.type_label.pack(anchor="w", padx=20, pady=(0, 2))
        self.type_row = tk.Frame(self)
        self.type_row.pack(anchor="w", padx=20, pady=(0, 10), fill="x")
        self.selected_agent_type = tk.StringVar(self)
        self.type_dropdown = tk.OptionMenu(self.type_row, self.selected_agent_type, "Seeker")
        self.type_dropdown.config(font=("Arial", 11), width=18)
        self.type_dropdown.pack(side="left")

        self.btn_left = tk.Frame(self)
        self.btn_left.pack(side="left", anchor="sw", padx=20, pady=15)
        self.btn_right = tk.Frame(self)
        self.btn_right.pack(side="right", anchor="se", padx=20, pady=15)
        self.spawn_btn = tk.Button(self.btn_left,text="Spawn",bg="#333333",fg="white",width=12,height=1,font=("Arial", 12),relief="raised",command=self.start_spawning)
        self.spawn_btn.pack(fill="x")
        self.stop_btn = tk.Button(self.btn_left,text="Stop Spawning",bg="#333333",fg="white",width=12,height=1,font=("Arial", 12),relief="raised",command=self.stop_spawning,state="disabled")
        self.stop_btn.pack(fill="x", pady=(8, 0))
        self.close_btn = tk.Button(self.btn_right,text="Close",bg="#333333",fg="white",width=10,height=1,font=("Arial", 12),relief="raised",command=self.close_popup)
        self.close_btn.pack(anchor="e")

        self.toggle_btn = tk.Button(self.type_row, textvariable=self.mode_var, font=("Arial", 12), width=10, relief="raised", command=self.toggle_mode)
        self.toggle_btn.pack(side="left", padx=(12, 0), pady=(0, 2))

        # Spawing varibles
        self.current_target_pos = None


        # run an update
        self.update_dropdown()
        self.spawning_state = tk.BooleanVar(self)
        self.spawning_state.set(False)

    def update_dropdown(self):
        '''Update the dropdown menu'''
        self.menu = self.type_dropdown["menu"]
        self.menu.delete(0, "end")
        if self.mode_var.get() == "Attacker":
            self.options = self.agent_type_attacker
        else:
            self.options = self.agent_type_defender

        for opt in self.options:
            self.menu.add_command(label=opt, command=lambda value=opt: self.selected_agent_type.set(value))
    
        if self.mode_var.get() == "Attacker":
            self.toggle_btn.config(bg="#8B0000", fg="white")
        else:
            self.toggle_btn.config(bg="#00008B", fg="white")
                       
        self.selected_agent_type.set(self.options[0])

    def toggle_mode(self):
        '''Toggle between the Attacker and Defender UAVs'''
        if self.mode_var.get() == "Attacker":
            self.mode_var.set("Defender")
        else:
            self.mode_var.set("Attacker")
        self.update_dropdown()

    def start_spawning(self):
        '''Enable spawning'''
        self.spawning_state.set(True)
        self.spawn_btn.config(text="Spawning", state="disabled")
        self.stop_btn.config(state="normal")
        # Only allow spawning of the selected type from the dropdown
        self.canvas.bind("<Button-1>", self.place_agent)
        self.parent.can_spawn = True

    def place_agent(self, event):
        '''Place agents on the canvas and store instructions'''
        if not self.spawning_state.get():
            print("NOT IN SPAWNING STATE-debug")
            return
        
        if self.parent.is_inside_map(event.x, event.y) is False:
            print("DEBUG- ADD CHECK TO DETERMIN IF CAN SPAWN ON LAND FOR CERTAIN AGENTS")
            return
        
        snap_x, snap_y, grid_x, grid_y = self.parent.snap_to_grid(event.x, event.y)
        grid_pos = (grid_x, grid_y)
        # add new agent
        agent_type = self.selected_agent_type.get()
        agent_name = self.name_entry.get() if self.name_entry.get() else agent_type
        new_agent_data = {
            'type': agent_type,
            'pos': grid_pos,
            'name': agent_name
            }

        if agent_type in self.parent.spawn_data:
            self.parent.spawn_data[agent_type].append(new_agent_data)
            # Update the agent display when a new agent is added
            self.parent.add_agent_to_display(agent_name, agent_type)
            self.parent.update_agent_info_label('seeker', self.parent.uuv_info_label)
            self.parent.update_agent_info_label('target', self.parent.target_info_label)
        else:
            print(f"ERROR: placed unknown agent type {agent_type}")
            return

        # DEBUG REMOVE
        print(self.selected_agent_type.get())
        self.draw_spawn_marker(snap_x, snap_y, 'green')
        print(f"Placed {agent_type} '{agent_name}' at grid {grid_pos} with data: {new_agent_data}")
  
    def stop_spawning(self):
        '''disable spawning'''
        self.spawning_state.set(False)
        self.spawn_btn.config(text="Spawn", state="normal")
        self.stop_btn.config(state="disabled")
        self.canvas.unbind("<Button-1>")
        self.parent.can_spawn = False

    def close_popup(self):
        '''Close the popup with rules'''
        self.stop_spawning()
        self.parent.popup_window = None
        self.destroy()

    def draw_spawn_marker(self, x, y, color):
        """Draws a marker circle on the canvas for user feedback."""
        radius = 5
        self.canvas.create_oval(
            x - radius, y - radius, 
            x + radius, y + radius, 
            fill=color, tags=("setup_marker")
        )