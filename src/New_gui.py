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
        self.logo_path = os.path.join(PARENT_DIR, "resources", "umass_logo.ico")
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
        self.agent_menu_button = tk.Button(self.agent_menu_section, text="Add Agent", command=None, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.start_button = tk.Button(self.sub_sim_section, text="▶ Start", command=None, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.reset_sim_button = tk.Button(self.sub_sim_section, text="Reset", command=None, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.exit_sim_button = tk.Button(self.sub_sim_section, text="Exit", command=None, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.file_button.pack(side='top', pady=4)
        self.agent_menu_button.pack(side='top')
        self.start_button.grid(row=0, column=0, padx=10, pady=5)
        self.reset_sim_button.grid(row=0, column=1, padx=10, pady=5)
        self.exit_sim_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # labels in menus
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


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_PATH)
App('simulation', (1100,600), PARENT_DIR)
