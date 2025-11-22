import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import os
from PIL import Image
from PIL import ImageTk 
from grid import Grid
from map import MapControl
from agents import model
from config import ConfigManager
from tkinter import messagebox as mb
from pathlib import Path

# go through and fix all the button bindings as they are over righting each other
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
        self.cell_count = 50

        # varibles for selection
        self.mouse_start_x = 0
        self.mouse_start_y = 0
        self.can_select = False

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
        #Add agent colors 
        self.agent_type_colors = {
            'Seeker': "#C60707",
            'Target': "#0600AA",
            'Detector': "#D209AA",
            'GA': "#781204",
        }
        # normalized lookup (case-insensitive)
        self._agent_type_colors_norm = {k.lower(): v for k, v in self.agent_type_colors.items()}

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
        #Create Agent Menu
        self.agent_menu = AgentMenu(parent=self, size=(440, 200))
        self.canvas_frame = CanvasFrame(self, self.canvas_size)
        self.popup_window = None

         # Create ConfigManager instance for saving/loading
        # Put configs in a local configs folder by default
        self.config_manager = ConfigManager(default_dir="configs", allow_overwrite=False)

        # sub-menus
        self.file_section = GeneralFrames(parent=self.menu, size=(440, 90), side='top', text='Map Selection')
        #Pack the agent menu into the menu
        self.agent_menu.pack(in_=self.menu, side='top', padx=5, pady=5)
        self.sim_options_section = GeneralFrames(parent=self.menu, size=(440, 150), side='top', text='Simulation Options')
        self.sub_sim_section = tk.Frame(self.sim_options_section)
        self.sub_sim_section.pack(expand=True)
        self.config_menu_section = GeneralFrames(parent=self.menu,size=(440,90),side='top',text="Config Options")
        self.sub_config_section = tk.Frame(self.config_menu_section)
        self.sub_config_section.pack(expand=True)
        

        #sub-menu buttons
        self.file_button = tk.Button(self.file_section, text="🌐 Select", command=self.select_file, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.start_button = tk.Button(self.sub_sim_section, text="▶ Start", command=self.on_start_click, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.reset_sim_button = tk.Button(self.sub_sim_section, text="🔄 Reset", command= lambda: self.reset_simulation(), bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.exit_sim_button = tk.Button(self.sub_sim_section, text="✕ Exit", command=self.destroy, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.analysis_button = tk.Button(self.sub_sim_section, text="⛶ Analysis", command=lambda: self.create_popup(2), bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.file_button.pack(side='top', pady=4)
        self.start_button.grid(row=0, column=0, padx=10, pady=5)
        self.reset_sim_button.grid(row=0, column=1, padx=10, pady=5)
        self.exit_sim_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.analysis_button.grid(row=1, column=1, padx=10, pady=5)
        self.save_button = tk.Button(self.sub_config_section, text="Save Config", bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised", command=self.save_config_dialog)
        self.load_button = tk.Button(self.sub_config_section, text="Load Config", bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised",  command=self.load_config_dialog)
        
        
        self.save_button.grid(row=0, column=0, padx=10, pady=5)
        self.load_button.grid(row=0, column=1, padx=10, pady=5)
        
        
        # labels in menus
        self.uuv_info_label = tk.Label(self.file_menu, text="Seekers: 0", font=("Arial", 11), anchor="w", justify="left")
        self.uuv_info_label.pack(fill="x", padx=10, pady=2)
        
        self.target_info_label = tk.Label(self.file_menu, text="Targets: 0", font=("Arial", 11), anchor="w", justify="left")
        self.target_info_label.pack(fill="x", padx=10, pady=2)

        self.coord_label = tk.Label(self.file_menu, text="Grid Position: (x, y) | [lat, lon]", font=("Arial", 11), anchor="w")
        self.coord_label.pack(fill="x", padx=10, pady=2)

        #TESTING FOR GRID SELECTION ADD SOMEWHERE LATER
        self.grid_button = tk.Button(self.file_menu, text="Select Grid", font=("Arial", 11), anchor="w", justify="left", command=lambda: self.select_grid_button())
        self.grid_button.pack(fill='x', padx=10, pady=2)

        # canvas settings
        self.canvas = CanvasMap(self.canvas_frame, (700,700))

        # control bindings
        self.canvas.bind("<Motion>", self.update_hover_info)

        # run
        self.mainloop()
    
    def select_grid_button(self):
        """updates the boolean values"""
        self.can_select=True
        self.can_spawn=False

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

    def draw_spawn_marker(self, x, y, color):
            """Draw a small circle marker on the main canvas and return the item id.

            x, y: pixel coordinates (same convention used elsewhere in the code).
            color: fill color string (e.g. '#C60707' or 'green').
            """
            radius = 5
            # ensure canvas exists
            if not hasattr(self, "canvas") or self.canvas is None:
                raise RuntimeError("Canvas not initialized; cannot draw spawn marker")
            item_id = self.canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=color, tags=("setup_marker",)
            )
            return item_id
    
    def build_spawns_from_gui(self) -> dict:
        """
        Convert the GUI's `self.spawn_data` into the `spawns` dict expected by UUVModel.process_spawn_data.

        Returns:
            dict mapping category -> list of spawn entries, where each entry is at least:
                {"type": <agent_type_str>, "pos": [x, y], ...optional fields...}
        Notes:
            - This is robust to case differences between GUI labels and model keys (e.g. "Seeker" vs "seeker" or "GA").
            - It preserves optional fields like "name" and "group_id" if present.
        """
        # Build mappings from agent type (lowercase) -> (type, category)
        type_to_category = {}
        type_lookup = {}
        for cat, types in model.UUVModel.AGENT_CATEGORIES.items():
            for t in types:
                type_to_category[t.lower()] = cat
                type_lookup[t.lower()] = t  # canonical form (keeps GA uppercase if used)

        # Initialize output categories
        spawns: dict = {cat: [] for cat in model.UUVModel.AGENT_CATEGORIES.keys()}

        # Iterate GUI spawn_data (keys may be canonical or user-facing)
        for key_type, entries in self.spawn_data.items():
            # normalize the key into a candidate agent type (string)
            key_type_str = str(key_type) if key_type is not None else ""
            for item in entries:
                # Extract pos and optional metadata
                if isinstance(item, (list, tuple)):
                    pos = list(item)
                    agent_type_guess = key_type_str
                    extras = {}
                elif isinstance(item, dict):
                    pos = item.get("pos")
                    agent_type_guess = item.get("type") or key_type_str
                    # copy optional extras
                    extras = {k: v for k, v in item.items() if k not in ("type", "pos")}
                else:
                    # unsupported entry type; skip
                    continue

                # Validate/normalize pos to [int, int]
                try:
                    pos_x = int(pos[0])
                    pos_y = int(pos[1])
                    pos = [pos_x, pos_y]
                except Exception:
                    # skip invalid positions
                    continue

                # Normalize agent type (case-insensitive lookup)
                agent_type_norm = str(agent_type_guess).strip()
                agent_type_lower = agent_type_norm.lower()
                canonical_type = type_lookup.get(agent_type_lower, agent_type_norm)

                # Determine category (fallback to 'attacker' if unknown)
                category = type_to_category.get(agent_type_lower, "attacker")

                # Build spawn entry
                spawn_entry = {"type": canonical_type, "pos": pos}
                # attach extras if present (name, group_id, color, etc.)
                for k, v in extras.items():
                    spawn_entry[k] = v

                spawns.setdefault(category, []).append(spawn_entry)

        # Remove empty categories
        spawns = {k: v for k, v in spawns.items() if v}
        return spawns

    def make_grid_validator(self):
        """
        Return a validate_fn(spawn_entry) -> (bool, Optional[str]) bound to current self.map_grid.

        validate_fn returns:
        - (True, None) if valid
        - (False, "reason") if invalid
        """
        g = getattr(self, "map_grid", None)
        if g is None:
            # No grid loaded: accept nothing
            def _no_grid_validator(entry):
                return False, "No grid loaded"
            return _no_grid_validator

        # Determine grid size robustly (support several Grid shapes)
        cols = rows = None

        # Preferred: Grid object exposes a 2D backing array `grid`
        grid_data = getattr(g, "grid", None)
        if grid_data is not None:
            try:
                rows = len(grid_data)
                cols = len(grid_data[0]) if rows > 0 else 0
            except Exception:
                rows = cols = None

        # Fallback: Grid created with `cells_n` for square grid
        if cols is None or rows is None:
            cells_n = getattr(g, "cells_n", None)
            if cells_n is not None:
                cols = rows = int(cells_n)

        # Last fallback: use width/height and cell_size
        if cols is None or rows is None:
            cell_size = getattr(g, "cell_size", None)
            width = getattr(g, "width", None) or getattr(g, "canvas_width", None)
            height = getattr(g, "height", None) or getattr(g, "canvas_height", None)
            if cell_size and width and height:
                cols = int(width / cell_size)
                rows = int(height / cell_size)

        if cols is None or rows is None:
            # If we still can't figure out bounds, return a validator that warns (fail-safe)
            def _unknown_size_validator(entry):
                return False, "Grid size unknown"
            return _unknown_size_validator

        # create final validator that also optionally checks cell-blocked state
        def _validator(entry):
            # entry expected: {"type": ..., "pos": [x,y], ...}
            pos = entry.get("pos")
            if not isinstance(pos, (list, tuple)) or len(pos) != 2:
                return False, "Invalid position format"
            try:
                x = int(pos[0])
                y = int(pos[1])
            except Exception:
                return False, "Position coordinates must be integers"

            if x < 0 or x >= cols or y < 0 or y >= rows:
                return False, f"Position out of bounds: ({x},{y}) not in [0..{cols-1}], [0..{rows-1}]"

            try:
                backing = getattr(g, "grid", None)
                if backing is not None:
                    cell_obj = backing[y][x]  # row=y, col=x
                    # If your blocked id is 1 like model.is_unblocked uses, check:
                    if hasattr(cell_obj, "id") and cell_obj.id == 1:
                        return False, f"Cell at ({x},{y}) is blocked"
            except Exception:
                # ignore cell-object checks if indexing fails
                pass

            return True, None

        return _validator

    def save_config_dialog(self):
        """
        Prompt user for a filename and save current GUI spawn config using ConfigManager.
        Uses self.build_spawns_from_gui() to build the payload.
        """
        # Build spawns dict
        spawns = self.build_spawns_from_gui()

        # Choose initial dir (fall back to cwd)
        try:
            initialdir = str(self.config_manager.config_dir)
        except Exception:
            initialdir = "."

        # Ask user where to save
        file_path = fd.asksaveasfilename(
            title="Save spawn config",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=initialdir,
        )
        if not file_path:
            return  # user cancelled

        # Save via ConfigManager
        try:
            saved_path, warnings = self.config_manager.save(spawns, path=Path(file_path))
        except FileExistsError as fe:
            mb.showerror("Save error", str(fe))
            return
        except Exception as e:
            mb.showerror("Save error", f"Failed to save config: {e}")
            return

        # Notify user and show non-fatal warnings if any
        if warnings:
            msg = f"Config saved to {saved_path}\n\nWarnings:\n" + "\n".join(warnings)
            mb.showwarning("Config saved with warnings", msg)
        else:
            mb.showinfo("Config saved", f"Config saved to {saved_path}")
  
    def load_config_dialog(self):
        file_path = fd.askopenfilename(title="Load spawn config", defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not file_path:
            return

        validator = self.make_grid_validator()
        cm = self.config_manager
        try:
            spawns, warnings, meta = cm.load(file_path, validate_fn=validator, remove_invalid=True)
        except Exception as e:
            mb.showerror("Load error", f"Failed to load config: {e}")
            return

        # present warnings and proceed
        if warnings:
            proceed = mb.askyesno("Load warnings", "Some entries were invalid or changed:\n\n" + "\n".join(warnings) + "\n\nProceed and import valid entries?")
            if not proceed:
                return

        applied = self.apply_loaded_spawns(spawns, wipe_existing=True)
        if applied:
            mb.showinfo("Load complete", "Configuration applied to map.")
        else:
            mb.showinfo("Load cancelled", "Configuration was not applied.")

    def apply_loaded_spawns(self, spawns: dict, wipe_existing: bool = True) -> bool:
        """
        Apply a loaded `spawns` dict to the GUI (place markers + update spawn_data and UI).

        Args:
            spawns: normalized dict returned by ConfigManager.load (category -> list of spawn entries).
                    Each entry must have at least "type" and "pos" ([x, y] grid coords).
            wipe_existing: if True, clear any existing GUI-placed agents before placing loaded ones.
                        If False and there are existing placements, the user will be asked whether to overwrite.

        Returns:
            True if placement succeeded (or was applied), False otherwise.
        """
        # 1) Refuse if simulation is running
        if getattr(self, "is_running", False):
            mb.showerror("Cannot place agents", "Please stop the simulation before applying a config.")
            return False

        # 2) Ensure map/grid present
        if self.map_grid is None:
            mb.showerror("No map/grid", "Please load/create a map before applying a spawn configuration.")
            return False

        # 3) If there are existing placed agents, confirm/clear them
        has_existing = any(len(lst) > 0 for lst in self.spawn_data.values())
        if has_existing and not wipe_existing:
            proceed = mb.askyesno("Overwrite existing agents?",
                                "There are already agents placed. Overwrite with loaded config?")
            if not proceed:
                return False

        if has_existing and wipe_existing:
            # Use existing reset routine to clear UI + model (it is safe and comprehensive)
            # reset_simulation stops animation, clears model and canvas items, and clears spawn_data / lists
            self.reset_simulation()

        # 4) Place loaded entries into spawn_data and draw markers
        cell_size = getattr(self.map_grid, "cell_size", None)
        if not cell_size:
            # fallback: if there's no cell_size, cannot compute marker coords
            mb.showerror("Grid error", "Grid cell size unknown; cannot draw spawn markers.")
            return False

        # Helper: find GUI key for a loaded type or create a new one if needed
        def find_type_key(t: str):
            if t in self.spawn_data:
                return t
            t_lower = str(t).lower()
            for key in list(self.spawn_data.keys()):
                if key.lower() == t_lower:
                    return key
            # not found: create a new key using the provided type string
            self.spawn_data.setdefault(t, [])
            return t

        # iterate and add spawns
        for category, entries in spawns.items():
            for entry in entries:
                t = entry.get("type")
                pos = entry.get("pos")
                if t is None or pos is None:
                    # skip malformed entry
                    continue

                # find matching key in spawn_data (case-insensitive)
                type_key = find_type_key(t)

                # create shallow copy to avoid mutating original loaded dict
                placed = dict(entry)

                # compute pixel coords for marker: grid_x * cell_size, grid_y * cell_size
                try:
                    grid_x = int(pos[0])
                    grid_y = int(pos[1])
                    px = grid_x * cell_size
                    py = grid_y * cell_size
                except Exception:
                    # skip invalid pos
                    continue

                # pick a color if provided, else from parent color map (case-insensitive)
                color = placed.get("color")
                if not color:
                    color = self._agent_type_colors_norm.get(str(t).lower())
                if not color:
                    color = "green"

                # draw marker and store marker_id
                try:
                    marker_id = self.draw_spawn_marker(px, py, color)
                    placed["marker_id"] = marker_id
                except Exception:
                    # still append spawn even if drawing fails
                    placed["marker_id"] = None

                # append to GUI spawn_data
                self.spawn_data.setdefault(type_key, []).append(placed)

        # 5) Rebuild agent_menu counts from spawn_data
        self.agent_menu.agent_display_data.clear()
        for t, entries in self.spawn_data.items():
            for e in entries:
                name = e.get("name") or t
                key = (name, t)
                self.agent_menu.agent_display_data[key] = self.agent_menu.agent_display_data.get(key, 0) + 1

        self.agent_menu.update_agent_listbox()

        # 6) Update info labels for the two shown types (use lowercased keys used by labels)
        # Try to update known labels; update_agent_info_label expects the agent_type exactly as used earlier ('seeker'/'target')
        self.update_agent_info_label('seeker', self.uuv_info_label)
        self.update_agent_info_label('target', self.target_info_label)

        return True

    def create_map(self):
        '''command for map/grid creation'''
        self.current_map = MapControl(
            shape_path=self.map_file_path,
            canvas=self.canvas,
            shallow_color=self.map_shallow_color,
            deep_color=self.map_deep_color
        )
        self.map_grid = Grid(width=self.canvas_size[0], height=self.canvas_size[1], cells_n=self.cell_count, canvas=self.canvas)
        self.canvas.config(background="#0A7005")
        # self.canvas.unbind("<Button-1>")

    def on_start_click(self):
        """Start / pause the simulation and create the mesa_model safely."""
        self.can_spawn = False
        self.can_select = False
        if not self.is_running:
            # Ensure canvas not bound to spawning
            # self.canvas.unbind("<Button-1>")
            # Provide immediate UI feedback
            self.start_button.config(state="disabled", bg="#333333", text="⏳ Starting...")

            # If model already exists, just resume it (do not clear/recreate)
            if self.mesa_model is None:
                # Validate map/grid preconditions
                if self.map_grid is None:
                    tk.messagebox.showerror("Error", "Please load a map before starting the simulation.")
                    self.start_button.config(state="normal", bg="#333333", text="▶ Start", command=self.on_start_click)
                    return

                # Create the model
                try:
                    viable_spawn_area = self.viable_spawn_select()
                    self.mesa_model = model.UUVModel(
                        spawns=self.spawn_data,
                        map=self.current_map,
                        grid=self.map_grid,
                        canvas=self.canvas,
                        viable_spawn=viable_spawn_area
                    )
                except Exception as e:
                    tk.messagebox.showerror("Error creating model", f"Failed to create simulation model:\n{e}")
                    # restore button state
                    self.mesa_model = None
                    self.start_button.config(state="normal", bg="#333333", text="▶ Start", command=self.on_start_click)
                    return
            else:
                pass

            # Start the animation loop
            self.is_running = True
            # Switch Start button to a Pause / Running state
            self.start_button.config(state="normal", bg="#333333", text="⏸ Running...", command=self.on_start_click)
            self.animate()

        else:
            # We are running -> pause/stop
            if self.animation_job:
                try:
                    self.after_cancel(self.animation_job)
                except Exception:
                    pass
                self.animation_job = None
            self.start_button.config(state="normal", bg="#333333", text="▶ Start", command=self.on_start_click)
            self.canvas_frame.config(bg="#333333")
            self.is_running = False
    
    def reset_simulation(self):
        """Fully stop and clear the running simulation and UI state."""
        # 1) Stop animation
        if self.animation_job:
            try:
                self.after_cancel(self.animation_job)
            except Exception:
                pass
            self.animation_job = None
        self.is_running = False

        # 2) If model exists, try to clear it
        if self.mesa_model is not None:
            if hasattr(self.mesa_model, "clear_agents"):
                try:
                    self.mesa_model.clear_agents()
                except Exception as e:
                    print("Warning: error while clearing model:", e)
            # drop reference so nothing calls it again
            self.mesa_model = None

        # 3) Clear related canvas items
        for item in self.canvas.find_all():
            tags = self.canvas.gettags(item)
            if "agent" in tags or "target" in tags or "setup_marker" in tags or "hover_rect" in tags or "detector" in tags or "search" in tags:
                self.canvas.delete(item)

        # 4) Clear GUI lists and spawn instructions
        self.agent_menu.agent_listbox.delete(0, tk.END)
        self.agent_menu.agent_display_data.clear()
        for agent_type in self.spawn_data:
            self.spawn_data[agent_type] = []

        # 5) Reset labels / buttons
        self.uuv_info_label.config(text="Seekers: 0")
        self.target_info_label.config(text="Targets: 0")
        self.coord_label.config(text="Grid Position: (x, y) | [lat, lon]")
        self.start_button.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=self.on_start_click)
        self.canvas_frame.config(bg="#333333")

        # 6) delete selection rect
        self.canvas.delete("spawn_sel")

    def animate(self):
        '''animate the screen'''
        if self.is_running and self.mesa_model is not None:
            self.animation_job = self.after(50, self.animate)
            self.mesa_model.step()
            # step through the model
        else:
            self.animation_job = None

    def create_popup(self,choice):
        '''create the popup window'''
        if self.popup_window is None and choice == 1:
            self.popup_window = UAVSelectWindow(self,"Select UAV", (400,300), self.canvas)
            self.can_select=False
            self.can_spawn=True
        elif self.popup_window is None and choice == 2:
            self.popup_window = AnalysisWindow(self,"Analysis",(1100,600), self.canvas)
            self.can_select=False
            self.can_spawn=True

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

    def viable_spawn_select(self):
        rect_ids = self.canvas.viable_spawn_pos()
        # print(f"rects: {rect_ids}")
        viable_spawns = list()
        for id in rect_ids:
            # get the top and bottom coords
            # print(f"rect id: {id}")
            coords = self.canvas.coords(id)
            x1, y1, x2, y2 = coords
            top_left = self.snap_to_grid(x1, y1)
            bottom_right = self.snap_to_grid(x2, y2)
            top_left = top_left[-2:]
            bottom_right = bottom_right[-2:]
            # print(f"top_left {top_left}, bottom_right {bottom_right}")

            for j in range(top_left[1], bottom_right[1]+1):
                for i in range(top_left[0], bottom_right[0]+1):
                    if self.map_grid.grid[j][i].id == 0:
                        spawn_point = (i, j)
                        if spawn_point not in viable_spawns:
                            viable_spawns.append(spawn_point)   
                            # print(f"({i}, {j})")
            # print(f"length {len(viable_spawns)}")
        return viable_spawns
    
        
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
        self.parent = parent
        self.width = size[0]
        self.height = size[1]
        self.pack(side='left', padx=self.padding, pady=self.padding)
        self.pack_propagate(False)
        
class CanvasMap(tk.Canvas):
    '''Handles the physcal canvas to draw on for simulation'''
    def __init__(self, parent, size):
        super().__init__(background="#040404", master=parent, width=size[0], height=size[1])
        self.pack()
        self.parent = parent
        self.pack_propagate(False)
        self.start_x=0
        self.start_y=0
        self.end_x=0
        self.end_y=0
        self.current_rect = None

        self.bind("<Button-1>", self.get_start_xy, add='+') #first press
        self.bind("<ButtonRelease-1>", self.get_end_xy, add='+') #release
        self.bind("<B1-Motion>", self.update_rectangle_mouse_drag, add='+') #update

    def get_start_xy(self, event): 
        """Get the coords for start x and start y"""
        # (start x, start y, end x, end y)
        print(f"can_select {self.parent.parent.can_select} and can_spawn {self.parent.parent.can_spawn}")
        if self.parent.parent.can_select is True and self.parent.parent.can_spawn is False:
            self.start_x, self.start_y, _, _ = self.parent.parent.snap_to_grid(event.x, event.y)
            self.current_rect=self.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='white', tags="spawn_sel")
            # self.start_x, self.start_y = event.x, event.y
        else:
            print("CAN NOT SELECT")

    def get_end_xy(self, event):
        """Get the coords for the end x and end y"""
        if self.parent.parent.can_select is True and self.parent.parent.can_spawn is False:
            self.current_rect = None
    
    def update_rectangle_mouse_drag(self, event):
        """Updates the selection rectangle on mouse drag"""
        if self.current_rect:
            self.end_x, self.end_y, _, _ = self.parent.parent.snap_to_grid(event.x, event.y)
            self.coords(self.current_rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def viable_spawn_pos(self):
        all_rect_ids = self.find_withtag("spawn_sel")
        # print(f"all spawn selections {all_rect_ids}")
        return all_rect_ids
    
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

class AgentMenu(tk.Frame):
    def __init__(self, parent, size,color=None):
        super().__init__(parent, width=size[0], height=size[1], bg=color, border=5,bd=2, relief='solid')
        self.pack(side='top', padx=5, pady=5)
        self.pack_propagate(False)

        # Title Label
        self.title = tk.Label(self, text="Agent Selection", font=("Arial", 13, "bold"))
        self.title.pack(side='top', pady=(0, 2))

        # Separator bar (like GeneralFrames)
        self.file_bar = tk.Frame(self, bg="black", height=2)
        self.file_bar.pack(side="top", fill="x", pady=(0, 8))

        #Agent Button
        self.agent_menu_button = tk.Button(self, text="+ Add Agent", command=lambda: self.create_popup(1), bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.agent_menu_button.pack(side='top',anchor='nw', pady=(0, 5))

        # Scrollbar, Listbox, and label setup
        self.agent_display_data = {}  # {(name, type): count}
        name_width = 10
        type_width = 8
        count_width = 4
        label_text = f"{'Name:':<{name_width}} {'Type:':<{type_width}} {'Count:':>{count_width}}"
        self.scrollbar_label = tk.Label(self, text=label_text, font=("Consolas", 12))
        self.scrollbar_label.pack(side='top', fill='y', anchor='nw', padx=(5,0), pady=(5,0))

        self.scrollbar = tk.Scrollbar(self)
        self.agent_listbox = tk.Listbox(self, font=("Consolas", 11), width=30, height=8)
        self.scrollbar.config(command=self.agent_listbox.yview)
        self.agent_listbox.config(yscrollcommand=self.scrollbar.set)
        self.agent_listbox.pack(side='left', fill='y', padx=(0, 2))
        self.scrollbar.pack(side='right', fill='y')

        #Scroll Bar Double click functionality
        self.agent_listbox_keys = [] #map listbox indices to keys for easier parsing
        self.agent_listbox.bind('<Double-3>',self._on_listbox_rdouble_click)
        self.agent_listbox.bind('<Double-1>',self._on_listbox_double_click)
        
        # Store reference to parent for callbacks
        self.parent = parent

    def create_popup(self,choice):
        # Call parent's popup creation method
        self.parent.create_popup(choice)

    #Moved from App class
    def update_agent_listbox(self):
        """Refresh the agent Listbox with current agent data."""
        self.agent_listbox.delete(0, tk.END)
        self.agent_listbox_keys = []
        # Set fixed widths for each column
        name_width = 12
        type_width = 10
        count_width = 4
        for (name, agent_type), count in self.agent_display_data.items():
            # Format each entry with fixed width columns
            entry = f"{name:<{name_width}} {agent_type:<{type_width}} {count:>{count_width}}"
            self.agent_listbox.insert(tk.END, entry)
            self.agent_listbox_keys.append((name, agent_type))
    #Moved from App class
    def add_agent_to_display(self, name, agent_type):
        """Add or update agent in the display dictionary."""
        key = (name, agent_type)
        if key in self.agent_display_data:
            self.agent_display_data[key] += 1
        else:
            self.agent_display_data[key] = 1
        self.update_agent_listbox()

    def _on_listbox_double_click(self, event):
        """Left button double click handler. Used to wipe selected agent via listbox"""
        try:
            idx = self.agent_listbox.nearest(event.y)
        except Exception:
            idx = None
        if idx is None:
            return
        # Ensure the index is valid
        if idx < 0 or idx >= len(self.agent_listbox_keys):
            return
        self.agent_listbox.selection_clear(0, tk.END)
        self.agent_listbox.selection_set(idx)
        name, agent_type = self.agent_listbox_keys[idx]

    def _on_listbox_rdouble_click(self, event):
        """Right-button double-click handler. Determine clicked index from event and open popup."""
        try:
            idx = self.agent_listbox.nearest(event.y)
        except Exception:
            idx = None
        if idx is None:
            return
        # Ensure the index is valid
        if idx < 0 or idx >= len(self.agent_listbox_keys):
            return
        # Make the clicked item the active/selected one (so UI shows selection)
        self.agent_listbox.selection_clear(0, tk.END)
        self.agent_listbox.selection_set(idx)
        name, agent_type = self.agent_listbox_keys[idx]
        count = self.agent_display_data.get((name, agent_type), 0)
        self._open_agent_detail_popup(name, agent_type, count)

    def _open_agent_detail_popup(self, name, agent_type, count):
        """Opens a popup window showing agent details (positions)."""
        popup = tk.Toplevel(self)
        popup.transient(self)
        popup.title(f"Agent Details")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)

        header = tk.Label(popup, text=f"{name} — {agent_type.title()} (count: {count})", font=("Consolas", 12, "bold"))
        header.pack(fill='x', padx=8, pady=(8,4))

        frame = tk.Frame(popup)
        frame.pack(fill='both', expand=True, padx=8, pady=(0,8))

        positions = self._get_positions_from_spawn_data(name, agent_type)
        if not positions:
            msg = tk.Label(frame, text="No positions found.", font=("Consolas", 11))
            msg.pack(anchor='w')
        else:
            for i, pos in enumerate(positions, start=1):
                pos_label = tk.Label(frame, text=f"{i}. {pos}", font=("Consolas", 11), anchor='w', justify='left')
                pos_label.pack(anchor='w')
        btn = tk.Button(popup, text="Close", command=popup.destroy, bg="#333333", fg="white", width=10, height=1, font=("Consolas", 12), relief="raised")
        btn.pack(pady=(0,8), padx=(0,8), anchor="se")

    def _get_positions_from_spawn_data(self, name, agent_type):
        positions = []
        spawn_dict = getattr(self.parent, "spawn_data", {})
        key_type = agent_type
        for t, spawn_list in spawn_dict.items():
            if str(t).lower() != str(key_type).lower():
                continue
            for spawn in spawn_list:
                spawn_name = spawn.get("name") or ""
                if spawn_name == name:
                    positions.append(spawn.get("pos"))
        return positions
class AnalysisWindow(tk.Toplevel):
    """Analysis popup window"""
    def __init__(self, parent, title, size, canvas):
        super().__init__(parent)
        #Initialize window
        self.parent = parent
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.attributes('-topmost', True)
        self.resizable(False,False)
        self.canvas = canvas
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Create a bordered container for the notebook so it has the same solid outline as GeneralFrames
        notebook_container = tk.Frame(self, bd=2, relief='solid', bg='black')
        notebook_container.pack(side='right', fill='both', expand=True, padx=(4,8), pady=8)
        notebook_container.pack_propagate(False)  # keep border/size stable

        # Add the small black top bar inside the container to match GeneralFrames' file_bar
        file_bar = tk.Frame(notebook_container, bg='black', height=4)
        file_bar.pack(side='top', fill='x')

        # Create a child frame inside the container to hold the Notebook itself (keeps the black border visible)
        notebook_inner = tk.Frame(notebook_container, bg=self.cget('bg'))
        notebook_inner.pack(fill='both', expand=True, padx=2, pady=(4,2))

        # Style the notebook tabs
        style = ttk.Style(self)
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        # Configure a custom style for this notebook and its tabs
        style_name = 'Analysis.TNotebook'
        tab_style = 'Analysis.TNotebook.Tab'
        style.configure(style_name,
                        background='#1c1c1c',     # notebook background
                        borderwidth=0)
        style.configure(tab_style,
                        background='#222222',     # tab background (unselected)
                        foreground='white',
                        padding=(10, 6),
                        font=('Arial', 10, 'bold'))
        # Set color for selected/active states
        style.map(tab_style,
                background=[('selected', '#000000'), ('active', '#333333')],
                foreground=[('selected', 'white')])

        #Set up left hand "Scenario Selection" menu 
        notebook_body = '#DCDAD5'  # same color used for notebook body

        # Outer black container so we get a solid black outline like GeneralFrames
        scenario_container = tk.Frame(self, bg='black', width=200, height=size[1])
        scenario_container.pack(side='left', padx=(8,4), pady=8)
        scenario_container.pack_propagate(False)

        # Inner panel that holds the actual content and uses the notebook body color
        self.scenario_select = tk.Frame(scenario_container, bg=notebook_body, width=194, height=size[1] - 20)
        self.scenario_select.pack(padx=2, pady=4, fill='y')
        self.scenario_select.pack_propagate(False)

        # Title and small black top bar (matches GeneralFrames)
        title = tk.Label(self.scenario_select, text="Scenario Selection", font=("Arial", 13, "bold"),
                         bg=notebook_body, fg='black')
        title.pack(side='top', pady=(8, 2))
        file_bar2 = tk.Frame(self.scenario_select, bg='black', height=2)
        file_bar2.pack(side='top', fill='x', pady=(0, 8))

        # Create the Notebook with the custom style and pack it inside the inner frame
        self.notebook = ttk.Notebook(notebook_inner, style=style_name)
        self.notebook.pack(fill='both', expand=True)

        # --- Tab frames ---
        self.tab_overview = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_overview, text='Overview')
        self.tab_metrics = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_metrics, text='Metrics')
        self.tab_cost = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cost, text='Cost')


    def close_window(self):
      self.parent.popup_window = None
      self.destroy()
    
class UAVSelectWindow(tk.Toplevel):
    '''UAV selecting popup window'''
    # Keep in the mind the grid pos and the way agents navigate is flipped
    def __init__(self, parent, title, size, canvas):
        super().__init__(parent)
        # setup the window 
        self.parent = parent
        self.title(title)
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


        #Set agent menu reference
        self.agent_menu = self.parent.agent_menu

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
        self.canvas.bind("<Button-1>", self.place_agent, add='+')
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
        #Obtain colors for agent from parent
        parent_colors = getattr(self.parent, "_agent_type_colors_norm", {})
        color_for_type = parent_colors.get(str(agent_type).lower(), "green")

        new_agent_data = {
            'type': agent_type,
            'pos': grid_pos,
            'name': agent_name,
            'color': color_for_type
            }
        

        if agent_type in self.parent.spawn_data:
            self.parent.spawn_data[agent_type].append(new_agent_data)
            # Update the agent display when a new agent is added
            self.agent_menu.add_agent_to_display(agent_name, agent_type)
            self.parent.update_agent_info_label('seeker', self.parent.uuv_info_label)
            self.parent.update_agent_info_label('target', self.parent.target_info_label)
        else:
            print(f"ERROR: placed unknown agent type {agent_type}")
            return

        # DEBUG REMOVE
        # print(self.selected_agent_type.get())
        marker_id = self.parent.draw_spawn_marker(snap_x, snap_y, color_for_type)
        new_agent_data['marker_id'] = marker_id
        
        #print(f"Placed {agent_type} '{agent_name}' at grid {grid_pos} with data: {new_agent_data}")

    def stop_spawning(self):
        '''disable spawning'''
        self.spawning_state.set(False)
        self.spawn_btn.config(text="Spawn", state="normal")
        self.stop_btn.config(state="disabled")
        # self.canvas.unbind("<Button-1>")
        self.parent.can_spawn = False

    def close_popup(self):
        '''Close the popup with rules'''
        self.stop_spawning()
        self.parent.popup_window = None
        self.destroy()
