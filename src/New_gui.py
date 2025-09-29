import tkinter as tk
from tkinter import filedialog as fd
import os
from PIL import Image
from PIL import ImageTk 
from grid import Grid
from map import MapControl

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


        # logo
        self.logo_path = os.path.join(parent_dir, "resources", "umass_logo.ico")
        self.logo_image = Image.open(self.logo_path)
        self.logo_icon = ImageTk.PhotoImage(self.logo_image)
        self.iconphoto(False, self.logo_icon)

        # menus
        self.menu = Menu(parent=self, size=(300, self.app_height),color='white')
        self.file_menu = FileMenu(self, (self.app_width, 100), color='white')
        self.canvas_frame = CanvasFrame(self, self.canvas_size)

        # sub-menus
        self.file_section = GeneralFrames(parent=self.menu, size=(440, 90), side='top', text='Map Selction')
        self.agent_menu_section = GeneralFrames(parent=self.menu, size=(440, 150), side='top', text='Agent Selection')
        self.sim_options_section = GeneralFrames(parent=self.menu, size=(440, 150), side='top', text='Simulation Options')
        self.sub_sim_section = tk.Frame(self.sim_options_section)
        self.sub_sim_section.pack(expand=True)

        #sub-menu buttons
        self.file_button = tk.Button(self.file_section, text="Select", command=self.select_file, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.agent_menu_button = tk.Button(self.agent_menu_section, text="Add Agent", command=self.show_agent_panel, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.start_button = tk.Button(self.sub_sim_section, text="▶ Start", command=self.on_start_click, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.reset_sim_button = tk.Button(self.sub_sim_section, text="Reset", command= lambda: self.reset_simulation(), bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.exit_sim_button = tk.Button(self.sub_sim_section, text="Exit", command=self.destroy, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.file_button.pack(side='top', pady=4)
        self.agent_menu_button.pack(side='top')
        self.start_button.grid(row=0, column=0, padx=10, pady=5)
        self.reset_sim_button.grid(row=0, column=1, padx=10, pady=5)
        self.exit_sim_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # labels in menus
        self.uuv_info_label = tk.Label(self.file_menu, text="UUVs: 0", font=("Arial", 11), anchor="w", justify="left")
        self.uuv_info_label.pack(fill="x", padx=10, pady=2)
        
        self.target_info_label = tk.Label(self.file_menu, text="Target: None", font=("Arial", 11), anchor="w", justify="left")
        self.target_info_label.pack(fill="x", padx=10, pady=2)

        self.coord_label = tk.Label(self.file_menu, text="Grid Position: (x, y) | [lat, lon]", font=("Arial", 11), anchor="w")
        self.coord_label.pack(fill="x", padx=10, pady=2)


        # canvas settings
        self.canvas = CanvasMap(self.canvas_frame, (700,700))

        # run
        self.mainloop()

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
        '''WORK IN PROGRESS'''
        self.disable_spawn_mode()
        if not is_running:
            self.canvas.unbind("<Button-1>")
            self.start_button.config(state="normal", bg="#333333", text="⏸ Running...", fg="white", command=self.on_start_click) 
            is_running = True
            self.animate()
        else:
            if animation_job:
                self.after_cancel(animation_job)
                animation_job = None
            self.start_button.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=self.on_start_click)
            self.canvas_frame.config(bg="#333333")
            is_running = False
    
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
        self.uuv_info_label.config(text="UUVs: 0")
        self.target_info_label.config(text="Target: None")
        self.coord_label.config(text="Grid Position: (x, y) | [lat, lon]")
        self.start_button.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=self.on_start_click)
        self.canvas_frame.config(bg="#333333")

    def animate(self):
        '''WORK IN PROGRESS'''
        if self.is_running and self.model_test is not None:
            self.model_test.step()
            self.animation_job = self.after(50, self.animate)
        else:
            self.animation_job = None

    def show_agent_panel(self):
        '''WORK IN PROGRESS'''
        # create the new window
        self.agent_window = tk.Toplevel(self)
        self.agent_window.title("Add Agent")
        self.agent_window.geometry("400x300")
        self.agent_window.resizable(False, False)

        self.mode_var = tk.StringVar(self.agent_window)
        self.mode_var.set("Attacker")
        self.name_label = tk.Label(self.agent_window, text="Name:", font=("Arial", 11))
        self.name_label.pack(anchor="w", padx=20, pady=(20, 2))
        self.name_entry = tk.Entry(self.agent_window, font=("Arial", 11), width=25)
        self.name_entry.pack(anchor="w", padx=20, pady=(0, 10))
        self.type_label = tk.Label(self.agent_window, text="Type:", font=("Arial", 11))
        self.type_label.pack(anchor="w", padx=20, pady=(0, 2))
        self.type_row = tk.Frame(self.agent_window)
        self.type_row.pack(anchor="w", padx=20, pady=(0, 10), fill="x")
        self.type_var = tk.StringVar(self.agent_window)
        self.type_dropdown = tk.OptionMenu(self.type_row, self.type_var, "Seeker")
        self.type_dropdown.config(font=("Arial", 11), width=18)
        self.type_dropdown.pack(side="left")

        self.btn_left = tk.Frame(self.agent_window)
        self.btn_left.pack(side="left", anchor="sw", padx=20, pady=15)
        self.btn_right = tk.Frame(self.agent_window)
        self.btn_right.pack(side="right", anchor="se", padx=20, pady=15)
        self.spawn_btn = tk.Button(self.btn_left,text="Spawn",bg="#333333",fg="white",width=12,height=1,font=("Arial", 12),relief="raised",command=self.start_spawning)
        self.spawn_btn.pack(fill="x")
        self.stop_btn = tk.Button(self.btn_left,text="Stop Spawning",bg="#333333",fg="white",width=12,height=1,font=("Arial", 12),relief="raised",command=self.stop_spawning,state="disabled")
        self.stop_btn.pack(fill="x", pady=(8, 0))
        self.close_btn = tk.Button(self.btn_right,text="Close",bg="#333333",fg="white",width=10,height=1,font=("Arial", 12),relief="raised",command=lambda: [self.stop_spawning(), self.agent_window.destroy()])
        self.close_btn.pack(anchor="e")
        
        self.toggle_btn = tk.Button(self.type_row, textvariable=self.mode_var, font=("Arial", 12), width=10, relief="raised", command=self.toggle_mode)
        self.toggle_btn.pack(side="left", padx=(12, 0), pady=(0, 2))
        self.update_dropdown()
        self.spawning_state = tk.BooleanVar(self.agent_window)
        self.spawning_state.set(False)

    def update_dropdown(self):
        '''WORK IN PROGRESS'''
        self.menu = self.type_dropdown["menu"]
        self.menu.delete(0, "end")
        if self.mode_var.get() == "Attacker":
            self.options = ["Seeker", "Detector"]
        else:
            self.options = ["Target"]

        for opt in self.options:
            self.menu.add_command(label=opt, command=lambda value=opt: self.type_var.set(value))
        self.type_var.set(self.options[0])
        if self.mode_var.get() == "Attacker":
            self.toggle_btn.config(bg="#8B0000", fg="white")
        else:
            self.toggle_btn.config(bg="#00008B", fg="white")

    def toggle_mode(self):
        '''WORK IN PROGRESS'''
        if self.mode_var.get() == "Attacker":
            self.mode_var.set("Defender")
        else:
            self.mode_var.set("Attacker")
        self.update_dropdown()
  
    def start_spawning(self):
        '''WORK IN PROGRESS'''
        self.spawning_state.set(True)
        self.spawn_btn.config(text="Spawning", state="disabled")
        self.start_button.config(state="normal")
        # Only allow spawning of the selected type from the dropdown
        self.canvas.bind("<Button-1>", self.place_agent)

    def place_agent(self, event):
        '''WORK IN PROGRESS'''
        if self.spawning_state.get():
            self.spawn_agent(self.name_entry.get(), self.type_var.get(), event.x, event.y)

    def stop_spawning(self):
        '''WORK IN PROGRESS'''
        self.spawning_state.set(False)
        self.spawn_btn.config(text="Spawn", state="normal")
        self.stop_btn.config(state="disabled")
        self.canvas.unbind("<Button-1>")


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
    def __init__(self, title, size):
        self.title=title
        self.geometry(f'{self.size[0]}x{self.size[1]}')
        self.attributes('-topmost', True)



CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_PATH)
App('simulation', (1100,600), PARENT_DIR)
