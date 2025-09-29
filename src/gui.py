import tkinter as tk
from tkinter import filedialog as fd
import numpy as np
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape
import os
from PIL import Image
from PIL import ImageTk 

# ---------------------------------------------------------------------------------
# How to Make a New Agent Spawnable via the Agent Panel (Step-by-Step Guide)
#
# 1. Create a New Spawner Class:
#    - Subclass AgentSpawner (see SeekerSpawner/TargetSpawner for examples).
#    - Implement the spawn(self, name, x, y) method with your custom logic.
#
# 2. Register Your Spawner:
#    - Add your spawner to the spawner_registry dictionary:
#      Example:
#      spawner_registry = {
#          "Seeker": lambda: SeekerSpawner(...),
#          "Target": lambda: TargetSpawner(...),
#          "MyAgent": lambda: MyAgentSpawner(...),  # <-- Add this line
#      }
#
# 3. Add to Agent Panel Dropdown:
#    - In show_agent_panel(), update the update_dropdown() function to include your agent type:
#      Example:
#      if mode_var.get() == "Attacker":
#          options = ["Seeker", "MyAgent"]  # <-- Add your agent here
#
# 4. Done!
#    - Your new agent type will now appear in the agent panel and can be spawned via the GUI.
#
# Note: If your agent is a "Defender", add it to the Defender options instead.
# ---------------------------------------------------------------------------------

# --- Agent Spawner Classes ---
class AgentSpawner:
    def __init__(self, canvas, test_grid, current_map, uuv_info_label, target_info_label, spawn_point, tracker, target_point, target_n, detector_spawn):
        self.canvas = canvas
        self.test_grid = test_grid
        self.current_map = current_map
        self.uuv_info_label = uuv_info_label
        self.target_info_label = target_info_label
        self.spawn_point = spawn_point
        self.tracker = tracker
        self.target_point = target_point
        self.target_n = target_n

        # i need to add a new varilbe everytime i add a new agent
        self.detector_n= [0]
        self.detector_spwn = detector_spawn

    def snap_to_grid(self, x, y):
        if self.test_grid is not None:
            grid_size = self.test_grid.cell_size
            snapped_x = round(x / grid_size) * grid_size
            snapped_y = round(y / grid_size) * grid_size
            grid_x = int(round(snapped_x / grid_size))
            grid_y = int(round(snapped_y / grid_size))
        else:
            snapped_x, snapped_y = x, y
            grid_x, grid_y = int(x), int(y)
        return snapped_x, snapped_y, grid_x, grid_y

    def is_inside_map(self, x, y):
        overlapping_items = self.canvas.find_overlapping(x, y, x, y)
        for item_id in overlapping_items:
            tags = self.canvas.gettags(item_id)
            if "map" in tags:
                return True
        return False

    def spawn(self, name, x, y):
        raise NotImplementedError

class SeekerSpawner(AgentSpawner):
    """Creates the seeker UAV"""
    def spawn(self, name, x, y):
        if not self.is_inside_map(x, y):
            print("Click not inside map area.")
            return
        if self.tracker[0] != 5:
            snapped_x, snapped_y, grid_x, grid_y = self.snap_to_grid(x, y)
            start = self.canvas.create_oval(snapped_x-5, snapped_y-5, snapped_x+5, snapped_y+5, fill="red", tags="agent")
            self.canvas.lift(start)
            self.tracker[0] += 1
            tmp_spw = [grid_y, grid_x]
            self.spawn_point.append(tmp_spw)
            uuvs_text = f"UUVs: {self.tracker[0]}   "
            uuvs_list = []
            for idx, spw in enumerate(self.spawn_point):
                lat, lon = self.current_map.canvas_to_latlon(spw[0], spw[1])
                uuvs_list.append(f"{idx+1}: [{lat:.3f}, {lon:.3f}]")
            lines = [", ".join(uuvs_list[i:i+3]) for i in range(0, len(uuvs_list), 3)]
            uuvs_text += "\n".join(lines)
            self.uuv_info_label.config(text=uuvs_text)

class TargetSpawner(AgentSpawner):
    """Creates the Target point"""
    def spawn(self, name, x, y):
        if not self.is_inside_map(x, y):
            print("Click not inside map area.")
            return
        if self.target_n[0] < 1:
            snapped_x, snapped_y, grid_x, grid_y = self.snap_to_grid(x, y)
            target = self.canvas.create_oval(snapped_x-5, snapped_y-5, snapped_x+5, snapped_y+5, fill="blue", tags="target")
            self.canvas.lift(target)
            self.target_n[0] = 1
            self.target_point[0] = [grid_y, grid_x]
            lat, lon = self.current_map.canvas_to_latlon(grid_y, grid_x)
            self.target_info_label.config(text=f"Target: [{lat:.3f}, {lon:.3f}]")

class DetectorSpawner(AgentSpawner):
    """Creates the Detector agents"""
    def spawn(self, name, x, y):
        if not self.is_inside_map(x, y):
            print("click not inside map area")
            return
        if self.detector_n[0] != 5:
            snapped_x, snapped_y, grid_x, grid_y = self.snap_to_grid(x, y)
            start = self.canvas.create_oval(snapped_x-1, snapped_y-1, snapped_x+1, snapped_y+1, fill="white", tags="detector")
            self.canvas.lift(start)
            self.detector_n[0] += 1
            tmp_spw = [grid_y, grid_x]
            self.detector_spwn.append(tmp_spw)



def run_gui(UUVModel, map, Grid):
    # For navigating the project
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_PATH)

    # Load the logo
    logo_path = os.path.join(PARENT_DIR, "resources", "umass_logo.ico")
    logo_image = Image.open(logo_path)

    # setup intial window
    root = tk.Tk()
    root.title("Simulation")
    app_width = 1100  # You can change this for the overall window
    app_height = 600  # You can change this for the overall window
    root.geometry(f'{app_width}x{app_height}')
    root.resizable(False, False)

    #Set logo as root window icon
    logo_photo = ImageTk.PhotoImage(logo_image)
    root.iconphoto(False, logo_photo)

    # frames and menus
    sim_menu = tk.Frame(root, width=300, height=app_height, border=5)  # You can change width here
    sim_menu.pack(side='right', padx=5, pady=5)
    sim_menu.pack_propagate(False)
    file_menu = tk.Frame(root, width=app_width, height=100, relief="flat",)
    file_menu.pack(side='bottom', padx=5, pady=5)
    file_menu.pack_propagate(False)
    uuv_info_label = tk.Label(file_menu, text="UUVs: 0", font=("Arial", 11), anchor="w", justify="left")
    uuv_info_label.pack(fill="x", padx=10, pady=2)

    # overlay_panel_attacker = tk.Frame(root, width=200, height=app_height, border=5)
    # overlay_panel_attacker.place_forget()  # Hide initially
    # overlay_panel_attacker.pack_propagate(False)

    # overlay_panel_defender = tk.Frame(root, width=200, height=app_height, border=5)
    # overlay_panel_defender.place_forget()  # Hide initially
    # overlay_panel_defender.pack_propagate(False)

    target_info_label = tk.Label(file_menu, text="Target: None", font=("Arial", 11), anchor="w", justify="left")
    target_info_label.pack(fill="x", padx=10, pady=2)

    coord_label = tk.Label(file_menu, text="Grid Position: (x, y) | [lat, lon]", font=("Arial", 11), anchor="w")
    coord_label.pack(fill="x", padx=10, pady=2)

    canvas_frame = tk.Frame(root, background='#333333', width=700, height=700, relief="raised", border=5)
    canvas_frame.pack(side='left',  padx=5, pady=5)
    canvas_frame.pack_propagate(False)  # Prevent frame from resizing to fit canvas

    canvas_width = 700  # Keep this fixed
    canvas_height = 700  # Keep this fixed
    canvas = tk.Canvas(background="#040404", master=canvas_frame, width=canvas_width, height=canvas_height)
    canvas.pack()
    canvas.pack_propagate(False)  # Prevent canvas from resizing

    # Define variables at the top level of run_gui so they can be used with nonlocal
    model_test = None
    is_running = False
    animation_job = None
    tracker = [0]
    target_n = [0]
    detector_n = [0]
    detector_spawn = []
    spawn_point = []
    target_point = [None]
    test_grid = None
    current_map = None
    file_path = None

    # Add a flag to control spawn mode
    spawn_mode_enabled = [False]

    """Dose nothing---Will be removed"""
    # def enable_spawn_mode():
    #     spawn_mode_enabled[0] = True
    #     canvas.bind("<Button-1>", handle_click)

    def disable_spawn_mode():
        spawn_mode_enabled[0] = False
        canvas.unbind("<Button-1>")

    # ------ Reset Function ---------
    def reset_simulation():
        nonlocal spawn_point, tracker, target_n, target_point, model_test, is_running, animation_job
        for item in canvas.find_all():
            tags = canvas.gettags(item)
            if "agent" in tags or "target" in tags or canvas.itemcget(item, "fill") in ["orange", "blue"]:
                canvas.delete(item)
        spawn_point = []
        tracker = [0]
        target_n = [0]
        target_point = [None]
        model_test = None
        if animation_job:
            root.after_cancel(animation_job)
            animation_job = None
        is_running = False
        uuv_info_label.config(text="UUVs: 0")
        target_info_label.config(text="Target: None")
        coord_label.config(text="Grid Position: (x, y) | [lat, lon]")
        start_btn.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=on_start_click)
        canvas_frame.config(bg="#333333")
        disable_spawn_mode()
        canvas.bind("<Button-1>", handle_click)

    """Dose nothing---Will be removed"""
    # def show_spawn_panel_attacker():
    #     x = sim_menu.winfo_x()
    #     y = sim_menu.winfo_y()
    #     width = sim_menu.winfo_width()
    #     height = sim_menu.winfo_height()
    #     overlay_panel_attacker.place(x=x, y=y, width=width, height=height)
    #     overlay_panel_attacker.lift()
    #     selected_option.set("detector")

    # def show_spawn_panel_defender():
    #     x = sim_menu.winfo_x()
    #     y = sim_menu.winfo_y()
    #     width = sim_menu.winfo_width()
    #     height = sim_menu.winfo_height()
    #     overlay_panel_defender.place(x=x, y=y, width=width, height=height)
    #     overlay_panel_defender.lift()
    #     selected_option.set("target")

    def show_agent_panel():
        agent_window = tk.Toplevel(root)
        agent_window.title("Add Agent")
        agent_window.geometry("400x300")
        agent_window.resizable(False, False)
        mode_var = tk.StringVar(agent_window)
        mode_var.set("Attacker")
        name_label = tk.Label(agent_window, text="Name:", font=("Arial", 11))
        name_label.pack(anchor="w", padx=20, pady=(20, 2))
        name_entry = tk.Entry(agent_window, font=("Arial", 11), width=25)
        name_entry.pack(anchor="w", padx=20, pady=(0, 10))
        type_label = tk.Label(agent_window, text="Type:", font=("Arial", 11))
        type_label.pack(anchor="w", padx=20, pady=(0, 2))
        type_row = tk.Frame(agent_window)
        type_row.pack(anchor="w", padx=20, pady=(0, 10), fill="x")
        type_var = tk.StringVar(agent_window)
        type_dropdown = tk.OptionMenu(type_row, type_var, "Seeker")
        type_dropdown.config(font=("Arial", 11), width=18)
        type_dropdown.pack(side="left")
        def update_dropdown():
            menu = type_dropdown["menu"]
            menu.delete(0, "end")
            if mode_var.get() == "Attacker":
                options = ["Seeker", "Detector"]
            else:
                options = ["Target"]

            for opt in options:
                menu.add_command(label=opt, command=lambda value=opt: type_var.set(value))
            type_var.set(options[0])
            if mode_var.get() == "Attacker":
                toggle_btn.config(bg="#8B0000", fg="white")
            else:
                toggle_btn.config(bg="#00008B", fg="white")
        def toggle_mode():
            if mode_var.get() == "Attacker":
                mode_var.set("Defender")
            else:
                mode_var.set("Attacker")
            update_dropdown()
        toggle_btn = tk.Button(
            type_row,
            textvariable=mode_var,
            font=("Arial", 12),
            width=10,
            relief="raised",
            command=toggle_mode
        )
        toggle_btn.pack(side="left", padx=(12, 0), pady=(0, 2))
        update_dropdown()
        spawning_state = tk.BooleanVar(agent_window)
        spawning_state.set(False)
        def start_spawning():
            spawning_state.set(True)
            spawn_btn.config(text="Spawning", state="disabled")
            stop_btn.config(state="normal")
            # Only allow spawning of the selected type from the dropdown
            def place_agent(event):
                if spawning_state.get():
                    spawn_agent(name_entry.get(), type_var.get(), event.x, event.y)
            canvas.bind("<Button-1>", place_agent)
        def stop_spawning():
            spawning_state.set(False)
            spawn_btn.config(text="Spawn", state="normal")
            stop_btn.config(state="disabled")
            canvas.unbind("<Button-1>")
        btn_left = tk.Frame(agent_window)
        btn_left.pack(side="left", anchor="sw", padx=20, pady=15)
        btn_right = tk.Frame(agent_window)
        btn_right.pack(side="right", anchor="se", padx=20, pady=15)
        spawn_btn = tk.Button(
            btn_left,
            text="Spawn",
            bg="#333333",
            fg="white",
            width=12,
            height=1,
            font=("Arial", 12),
            relief="raised",
            command=start_spawning
        )
        spawn_btn.pack(fill="x")
        stop_btn = tk.Button(
            btn_left,
            text="Stop Spawning",
            bg="#333333",
            fg="white",
            width=12,
            height=1,
            font=("Arial", 12),
            relief="raised",
            command=stop_spawning,
            state="disabled"
        )
        stop_btn.pack(fill="x", pady=(8, 0))
        close_btn = tk.Button(
            btn_right,
            text="Close",
            bg="#333333",
            fg="white",
            width=10,
            height=1,
            font=("Arial", 12),
            relief="raised",
            command=lambda: [stop_spawning(), agent_window.destroy()]
        )
        close_btn.pack(anchor="e")


    def spawn_agent(name, agent_type, x=None, y=None):
        """Uses the custom classes spawns to create agents"""
        nonlocal spawn_point, tracker, target_point, target_n, test_grid, current_map
        if x is not None and y is not None:
            if agent_type in spawner_registry:
                # Always get a fresh spawner with current references
                spawner = spawner_registry[agent_type]()
                spawner.spawn(name, x, y)
                print(spawner)
            else:
                print(f"Unknown agent type: {agent_type}")
        else:
            print(f"Ready to spawn {agent_type} named '{name}' (waiting for click)")
        

    # --- Agent Spawner Registry ---
    spawner_registry = {
        "Seeker": lambda: SeekerSpawner(canvas, test_grid, current_map, uuv_info_label, target_info_label, spawn_point, tracker, target_point, target_n, detector_spawn),
        "Target": lambda: TargetSpawner(canvas, test_grid, current_map, uuv_info_label, target_info_label, spawn_point, tracker, target_point, target_n, detector_spawn),
        "Detector" : lambda: DetectorSpawner(canvas, test_grid, current_map, uuv_info_label, target_info_label, spawn_point, tracker, target_point, target_n, detector_spawn)
    }

    # This is the were the agent model starts
    def on_start_click():
        '''Start button controles this'''
        nonlocal is_running, animation_job, model_test, test_grid
        disable_spawn_mode()
        if not is_running:
            canvas.unbind("<Button-1>")
            start_btn.config(state="normal", bg="#333333", text="⏸ Running...", fg="white", command=on_start_click) 
            if model_test is None:
                if 'test_grid' not in locals() and 'test_grid' not in globals() or test_grid is None:
                    tk.messagebox.showerror("Error", "Please load a map before starting the simulation.")
                    start_btn.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=on_start_click)
                    return
                if target_point[0] is None:
                    tk.messagebox.showerror("Error", "Please spawn a target before starting the simulation.")
                    start_btn.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=on_start_click)
                    return
                print(detector_spawn)
                model_test = UUVModel(
                    n=tracker[0],
                    canvas=canvas,
                    spawns=spawn_point.copy(),
                    targets=target_point[0],
                    map=current_map,
                    grid=test_grid.grid,
                    detector_spawn=detector_spawn,
                    detector_n=detector_n[0]
                )
            is_running = True
            animate()
        else:
            if animation_job:
                root.after_cancel(animation_job)
                animation_job = None
            start_btn.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=on_start_click)
            canvas_frame.config(bg="#333333")
            is_running = False
            canvas.bind("<Button-1>", handle_click)

    def animate():
        nonlocal animation_job
        if is_running and model_test is not None:
            model_test.step()
            animation_job = root.after(50, animate)
        else:
            animation_job = None

    selected_option = tk.StringVar()
    selected_option.set("uuv")

    def set_spawn_mode(mode):
        selected_option.set(mode)



    file_path = None
    def select_file():
        nonlocal file_path
        file_path = fd.askopenfilename(title="Selct a shapfile",
                                   initialdir="/", 
                                   filetypes=[("Shape files", "*.shp")]
                                    )
        if file_path:
            print(f"Selcted file: {file_path}")
            create_map(file_path)
        else:
            print("no file selected")

    def check_inside_map(event):
        overlapping_items = canvas.find_overlapping(event.x, event.y, event.x, event.y)
        is_inside_tag = False
        for item_id in overlapping_items:
            tags = canvas.gettags(item_id)
            if "map" in tags:
                is_inside_tag = True
                break
        return is_inside_tag

    def handle_click(event):
        print("dost this do somthing?")
        nonlocal spawn_point, tracker, target_n, target_point, selected_option, test_grid, detector_spawn, detector_n
        if not spawn_mode_enabled[0]:
            return
        is_inside_tag = check_inside_map(event=event)
        if is_inside_tag == True:
            if 'test_grid' in locals() or 'test_grid' in globals():
                grid_size = test_grid.cell_size
                snapped_x = round(event.x / grid_size) * grid_size
                snapped_y = round(event.y / grid_size) * grid_size
                grid_x = int(round(snapped_x / grid_size))
                grid_y = int(round(snapped_y / grid_size))
            else:
                snapped_x = event.x
                snapped_y = event.y
                grid_x = int(event.x)
                grid_y = int(event.y)
            agent_type = selected_option.get()
            if agent_type == "uuv":
                if tracker[0] != 5:
                    start = canvas.create_oval(snapped_x-5, snapped_y-5, snapped_x + 5, snapped_y +5, fill="red", tags="agent")
                    canvas.lift(start)
                    tracker[0] += 1
                    tmp_spw = [grid_y, grid_x]
                    spawn_point.append(tmp_spw)
                    uuvs_text = f"UUVs: {tracker[0]}   "
                    uuvs_list = []
                    for idx, spw in enumerate(spawn_point):
                        lat, lon = current_map.canvas_to_latlon(spw[0], spw[1])
                        uuvs_list.append(f"{idx+1}: [{lat:.3f}, {lon:.3f}]")
                    lines = [", ".join(uuvs_list[i:i+3]) for i in range(0, len(uuvs_list), 3)]
                    uuvs_text += "\n".join(lines)
                    uuv_info_label.config(text=uuvs_text)
            elif agent_type == "target":
                if target_n[0] != 1:
                    target = canvas.create_oval(snapped_x-5, snapped_y-5, snapped_x+5, snapped_y+5, fill="blue", tags="target")
                    canvas.lift(target)
                    target_n[0] = 1
                    target_point[0] = [grid_y, grid_x]
                    lat, lon = current_map.canvas_to_latlon(target_point[0], target_point[1])
                    target_info_label.config(text=f"Target: [{lat:.3f}, {lon:.3f}]")
            elif agent_type == "detector":
                if detector_n[0] != 5:
                    detector_n[0] += 1
                    canvas.create_oval(snapped_x-1, snapped_y-1, snapped_x+1, snapped_y+1, fill="white", tags="detector")
                    tmp_spw = [grid_y, grid_x]
                    detector_spawn.append(tmp_spw)

    def show_depth(event):
        current_map.depth_loc(event.x, event.y)

    def update_hover_info(event):
        nonlocal test_grid, current_map
        if 'test_grid' in locals() or 'test_grid' in globals():
            grid_size = test_grid.cell_size
            snapped_x = round(event.x / grid_size)
            snapped_y = round(event.y / grid_size)
            if current_map is not None and hasattr(current_map, "canvas_to_latlon"):
                lat, lon = current_map.canvas_to_latlon(snapped_y * grid_size, snapped_x * grid_size)
                coord_label.config(text=f"Grid Position: ({snapped_x}, {snapped_y}) | [{lat:.3f}, {lon:.3f}]")
            else:
                coord_label.config(text="Grid Position: (x, y) | [lat, lon]")
            canvas.delete("hover_rect")
            x1 = snapped_x * grid_size - grid_size / 2
            y1 = snapped_y * grid_size - grid_size / 2
            x2 = x1 + grid_size
            y2 = y1 + grid_size
            canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=2, tags="hover_rect")

    canvas.bind("<Button-1>", handle_click)
    canvas.bind("<Button-3>", show_depth)
    canvas.bind("<Motion>", update_hover_info)

    file_section = tk.Frame(sim_menu, bd=2, relief="solid", padx=5, pady=5, width=440, height=90)
    file_section.pack(side="top", pady=8, anchor="sw")
    file_section.pack_propagate(False)
    file_title = tk.Label(file_section, text="Map Selection", font=("Arial", 13, "bold"))
    file_title.pack(side="top", fill="x", pady=(0, 2))
    file_bar = tk.Frame(file_section, bg="black", height=2)
    file_bar.pack(side="top", fill="x", pady=(0, 8))

    model_section = tk.Frame(sim_menu, bd=2, relief="solid", padx=5, pady=5, width=440, height=150)
    model_section.pack(side="top", pady=8)
    model_section.pack_propagate(False)
    model_title = tk.Label(model_section, text="Agent Selection", font=("Arial", 13, "bold"))
    model_title.pack(side="top", fill="x", pady=(0, 2))
    model_bar = tk.Frame(model_section, bg="black", height=2)
    model_bar.pack(side="top", fill="x", pady=(0, 8))

    agent_list_frame = tk.Frame(model_section, bd=2, relief="solid", padx=6, pady=6)
    agent_list_frame.pack(side="top", fill="x", padx=9, pady=8)

    header_name = tk.Label(agent_list_frame, text="Name", font=("Arial", 11, "bold"), borderwidth=1, relief="solid", width=10)
    header_type = tk.Label(agent_list_frame, text="Type", font=("Arial", 11, "bold"), borderwidth=1, relief="solid", width=10)
    header_num = tk.Label(agent_list_frame, text="#", font=("Arial", 11, "bold"), borderwidth=1, relief="solid", width=8)
    header_name.grid(row=0, column=0, sticky="nsew")
    header_type.grid(row=0, column=1, sticky="nsew")
    header_num.grid(row=0, column=2, sticky="nsew")

    example_name = tk.Label(agent_list_frame, text="UUV", font=("Arial", 11), borderwidth=1, relief="solid", width=10)
    example_type = tk.Label(agent_list_frame, text="Seeker", font=("Arial", 11), borderwidth=1, relief="solid", width=10)
    example_num = tk.Label(agent_list_frame, text="5", font=("Arial", 11), borderwidth=1, relief="solid", width=8)
    example_name.grid(row=1, column=0, sticky="nsew")
    example_type.grid(row=1, column=1, sticky="nsew")
    example_num.grid(row=1, column=2, sticky="nsew")
    # def update_agent_list(agent_data):
    #     for widget in agent_list_frame.winfo_children():
    #         if widget.grid_info()["row"] != 0:
    #             widget.destroy()
    #     for i, agent in enumerate(agent_data, start=1):
    #         tk.Label(agent_list_frame, text=agent["name"], font=("Arial", 11), borderwidth=1, relief="solid", width=16).grid(row=i, column=0, sticky="nsew")
    #         tk.Label(agent_list_frame, text=agent["type"], font=("Arial", 11), borderwidth=1, relief="solid", width=16).grid(row=i, column=1, sticky="nsew")
    #         tk.Label(agent_list_frame, text=str(agent["num"]), font=("Arial", 11), borderwidth=1, relief="solid", width=8).grid(row=i, column=2, sticky="nsew")
    
    sim_options = tk.Frame(sim_menu, bd=2, relief="solid", padx=5, pady=5, width=440, height=150)
    sim_options.pack(side="top", pady=8, anchor="sw")  
    sim_options.pack_propagate(False)
    sim_options_title = tk.Label(sim_options, text="Simulation Options", font=("Arial", 13, "bold"))
    sim_options_title.pack(side="top", fill="x", pady=(0, 2))
    sim_options_bar = tk.Frame(sim_options, bg="black", height=2)
    sim_options_bar.pack(side="top", fill="x", pady=(0, 8))
    sim_options_btn_frame = tk.Frame(sim_options)
    sim_options_btn_frame.pack(expand=True)
    file_button = tk.Button(
        file_section,
        text="Select",
        command=select_file,
        bg="#333333",
        fg="white",
        width=10,
        height=1,
        font=("Arial", 12),
        relief="raised"
    )
    model_button = tk.Button(
        model_section,
        text="Add Agent",
        command=show_agent_panel,
        bg="#333333",
        fg="white",
        width=10,
        height=1,
        font=("Arial", 12),
        relief="raised"
    )
    start_btn = tk.Button(
        sim_options_btn_frame,
        text="▶ Start",
        command=on_start_click,
        bg="#333333",
        fg="white",
        width=10,
        height=1,
        font=("Arial", 12)
    )
    reset_btn = tk.Button(
        sim_options_btn_frame,
        text="Reset",
        bg="#333333",
        fg="white",
        width=10,
        height=1,
        font=("Arial", 12),
        relief="raised",
        command=lambda: reset_simulation()
    )
    exit_btn = tk.Button(
        sim_options_btn_frame,
        text="Exit",
        bg="#333333",
        fg="white",
        width=10,
        height=1,
        font=("Arial", 12),
        relief="raised",
        command=root.destroy
    )
    file_button.pack(side="top", pady=4)
    model_button.pack(side="top", anchor="nw")
    start_btn.grid(row=0, column=0, padx=10, pady=5)
    reset_btn.grid(row=0, column=1, padx=10, pady=5)
    exit_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
    # spawn_uuv_radio = tk.Radiobutton(
    #     overlay_panel_attacker,
    #     text="Spawn UUV",
    #     variable=selected_option,
    #     value="uuv",
    #     bg="#333333",
    #     fg="white",
    #     selectcolor="#333333",
    #     width=15,
    #     height=1,
    #     font=("Arial", 16),
    #     relief="raised"
    # )
    # exit_overlay_btn_attacker = tk.Button(
    #     overlay_panel_attacker,
    #     text="Back",
    #     bg="#F70C03",
    #     fg="white",
    #     width=15,
    #     height=1,
    #     font=("Arial", 16),
    #     relief="raised",
    #     command=lambda: overlay_panel_attacker.place_forget()
    # )
    # spawn_uuv_radio.pack(side="top", pady=10)
    # exit_overlay_btn_attacker.pack(side="bottom", pady=5)
    # spawn_target_radio = tk.Radiobutton(
    #     overlay_panel_defender,
    #     text="Spawn Target",
    #     variable=selected_option,
    #     value="target",
    #     bg="#333333",
    #     fg="white",
    #     selectcolor="#333333",
    #     width=15,
    #     height=1,
    #     font=("Arial", 16),
    #     relief="raised"
    # )



    # exit_overlay_btn_defender = tk.Button(
    #     overlay_panel_defender,
    #     text="Back",
    #     bg="#F70C03",
    #     fg="white",
    #     width=15,
    #     height=1,
    #     font=("Arial", 16),
    #     relief="raised",
    #     command=lambda: overlay_panel_defender.place_forget()
    # )
    # spawn_target_radio.pack(side="top", pady=10)
    # exit_overlay_btn_defender.pack(side="bottom", pady=10)
    # tk.Label(sim_menu, text="", height=2).pack(side="top")
    # current_map = None


    def create_map(shape_path):
        shallow_color = (170, 201, 250)
        deep_color = (0, 0, 26)
        nonlocal current_map
        current_map = map.MapControl(
            shape_path=shape_path,
            canvas=canvas,
            shallow_color=shallow_color,
            deep_color=deep_color
        )
        create_grid()
        canvas.config(background="#0A7005")
        canvas.unbind("<Button-1>")
    def animate():
        nonlocal animation_job
        if is_running and model_test is not None:
            model_test.step()
            animation_job = root.after(50, animate)
        else:
            animation_job = None
    def create_grid():
        nonlocal test_grid
        test_grid = Grid(width=canvas_width, height=canvas_height, cells_n=50, canvas=canvas)
    test_grid = None
    root.mainloop()
