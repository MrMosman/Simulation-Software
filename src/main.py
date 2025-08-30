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

# project imports
from agents.model import UUVModel
import map
from grid import Grid

# For navigating the project
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_PATH)

# Load the logo
logo_path = os.path.join(PARENT_DIR, "resources", "umass_logo.ico")
logo_image = Image.open(logo_path)

# setup intial window
root = tk.Tk()
root.title("fixing agents, adding placement, starting")
app_width = 800
app_height = 600
root.geometry(f'{app_width}x{app_height}')
root.resizable(False, False)

#Set logo as root window icon
logo_photo = ImageTk.PhotoImage(logo_image)
root.iconphoto(False, logo_photo)

# frames and menus
sim_menu = tk.Frame(root, width=200, height=app_height, border=5)
sim_menu.pack(side='left', padx=5, pady=5)
sim_menu.pack_propagate(False)
file_menu = tk.Frame(root, width=app_width, height=100, relief="flat",)
file_menu.pack(side='bottom', padx=5, pady=5)
file_menu.pack_propagate(False)
uuv_info_label = tk.Label(file_menu, text="UUVs: 0", font=("Arial", 11), anchor="w", justify="left")
uuv_info_label.pack(fill="x", padx=10, pady=2)

overlay_panel_attacker = tk.Frame(root, width=200, height=app_height, border=5)
overlay_panel_attacker.place_forget()  # Hide initially
overlay_panel_attacker.pack_propagate(False)

overlay_panel_defender = tk.Frame(root, width=200, height=app_height, border=5)
overlay_panel_defender.place_forget()  # Hide initially
overlay_panel_defender.pack_propagate(False)

target_info_label = tk.Label(file_menu, text="Target: None", font=("Arial", 11), anchor="w", justify="left")
target_info_label.pack(fill="x", padx=10, pady=2)

coord_label = tk.Label(file_menu, text="Grid Position: (x, y) | [lat, lon]", font=("Arial", 11), anchor="w")
coord_label.pack(fill="x", padx=10, pady=2)

# ---gridlabel---
# coord_label = tk.Label(sim_menu, text="Grid Position: (x, y)")
# coord_label.pack(side="top", pady=10)

# Remove mouse_info_label definition and packing
# mouse_info_label = tk.Label(file_menu, text="Mouse: None", font=("Arial", 11), anchor="w")
# mouse_info_label.pack(fill="x", padx=10, pady=2)
canvas_frame = tk.Frame(root, background='green', width=700, height=700, relief="raised", border=5)
canvas_frame.pack(side='top',  padx=5, pady=5)

canvas_width = 700
canvas_height = 700
canvas = tk.Canvas(background="#040404", master=canvas_frame, width=canvas_width, height=canvas_height)  # Initial background black
canvas.pack()
#---------Mouse cursor coordinate function---------------
def update_mouse_position(event):
    # Remove contents, or leave as a stub if still bound elsewhere
    pass
canvas.bind("<Motion>", update_mouse_position)

# Add a global to track simulation state
is_running = False
animation_job = None

# ------ Reset Function ---------
def reset_simulation():
    global spawn_point, tracker, target_n, target_point, model_test, is_running, animation_job

    # Remove all UUV and target ovals from the canvas
    for item in canvas.find_all():
        tags = canvas.gettags(item)
        if "agent" in tags or "target" in tags or canvas.itemcget(item, "fill") in ["orange", "blue"]:
            canvas.delete(item)

    # Reset variables
    spawn_point = []
    tracker = 0
    target_n = 0
    target_point = None
    model_test = None
    # Cancel animation if running
    if animation_job:
        root.after_cancel(animation_job)
        animation_job = None
    is_running = False
    # Reset info labels
    uuv_info_label.config(text="UUVs: 0")
    target_info_label.config(text="Target: None")
    coord_label.config(text="Grid Position: (x, y) | [lat, lon]")

    # Reset start button
    start_btn.config(state="normal", bg="green", text="Start", fg="white", command=on_start_click)

    # Reset canvas frame color
    canvas_frame.config(bg="green")

    # Rebind mouse click event so you can spawn UUVs/targets again
    canvas.bind("<Button-1>", handle_click)

def show_spawn_panel_attacker():
    overlay_panel_attacker.place(x=5, y=5, width=200, height=app_height)
    overlay_panel_attacker.lift()  # Bring the overlay panel to the top
    selected_option.set("uuv")     # Ensure UUV radio is highlighted

def show_spawn_panel_defender():
    overlay_panel_defender.place(x=5, y=5, width=200, height=app_height)
    overlay_panel_defender.lift()  # Bring the overlay panel to the top
    selected_option.set("target")  # Ensure Target radio is highlighted

# ----buttton control----
# start simulation
spawn_point = []
target_point = None
def on_start_click():
    global is_running, animation_job, model_test
    if not is_running:
        # Resume simulation if model_test exists, otherwise start new
        canvas.unbind("<Button-1>")
        start_btn.config(state="normal", bg="#005000", text="⏸ Running...", fg="white", command=on_start_click)  # Dark green
        canvas_frame.config(bg="#005000")  # Change border to dark green when running
        global spawn_point
        if model_test is None:
            # print(spawn_point)
            model_test = UUVModel(
                n=tracker,
                canvas=canvas,
                spawns=spawn_point,
                targets=target_point,
                map=current_map,
                grid=test_grid.grid
            )
        is_running = True
        # Start animation loop immediately and keep it running
        animate()
    else:
        # Pause simulation
        if animation_job:
            root.after_cancel(animation_job)
            animation_job = None
        start_btn.config(state="normal", bg="green", text="▶ Start", fg="white", command=on_start_click)  # Play symbol
        canvas_frame.config(bg="green")
        is_running = False
        # Re-enable UUV/target placement when paused
        canvas.bind("<Button-1>", handle_click)

def animate():
    global animation_job
    if is_running and model_test is not None:
        model_test.step()
        animation_job = root.after(50, animate)
    else:
        animation_job = None

# =========================
# RADIO BUTTON VARIABLE (must be before any radio/button using it)
# =========================
selected_option = tk.StringVar()
selected_option.set("uuv")

def set_spawn_mode(mode):
    selected_option.set(mode)

# =========================
# GLOBALS FOR SPAWN TRACKING
# =========================
tracker = 0
target_n = 0
spawn_point = []
target_point = None
model_test = None  # <-- Ensure this is defined globally

# =========================
# Function Definitions Needed for Buttons
# =========================

file_path = None
def select_file():
    """selects file-only allow shape files"""
    global file_path
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
    """Get a list of items to determine if within boundaries"""
    overlapping_items = canvas.find_overlapping(event.x, event.y, event.x, event.y)
    is_inside_tag = False
    for item_id in overlapping_items:
        tags = canvas.gettags(item_id)
        if "map" in tags:
            is_inside_tag = True
            break
    return is_inside_tag


# radion fuctions
tracker = 0
target_n = 0
def handle_click(event):
    """
    Handles the spawning of UUV and target points and updates info labels, snapping them to the grid.
    Their positions are stored as grid indices, not pixel coordinates.
    """
    global spawn_point
    global tracker
    global target_n
    global target_point
    global selected_option
    global test_grid

    is_inside_tag = check_inside_map(event=event)

    if is_inside_tag == True:
        # Check if the grid object exists before trying to access its attributes
        if 'test_grid' in globals() and test_grid is not None:
            grid_size = test_grid.cell_size
            
            # Snap the clicked pixel coordinates to the nearest grid point
            snapped_x = round(event.x / grid_size) * grid_size
            snapped_y = round(event.y / grid_size) * grid_size

            # Convert the snapped pixel coordinates to grid indices
            # The indices are the row and column in the 2D list
            grid_x = int(round(snapped_x / grid_size))
            grid_y = int(round(snapped_y / grid_size))
        else:
            # Fallback to pixel coordinates if the grid is not yet created
            snapped_x = event.x
            snapped_y = event.y
            grid_x = int(event.x)
            grid_y = int(event.y)

        if selected_option.get() == "uuv":
            if tracker != 5:
                # Use the snapped pixel coordinates for drawing the circle on the canvas
                start = canvas.create_oval(snapped_x-5, snapped_y-5, snapped_x + 5, snapped_y +5, fill="red", tags="agent")  # UUVs red
                canvas.lift(start)
                tracker += 1
                # Store the grid indices in the spawn_point list
                tmp_spw = [grid_y, grid_x]
                # print(test_grid.grid[grid_y][grid_x])
                spawn_point.append(tmp_spw)
                # Update UUV info label
                uuvs_text = f"UUVs: {tracker}   "
                uuvs_list = []
                for idx, spw in enumerate(spawn_point):
                    lat, lon = current_map.canvas_to_latlon(spw[0], spw[1])
                    uuvs_list.append(f"{idx+1}: [{lat:.3f}, {lon:.3f}]")
                lines = [", ".join(uuvs_list[i:i+3]) for i in range(0, len(uuvs_list), 3)]
                uuvs_text += "\n".join(lines)
                uuv_info_label.config(text=uuvs_text)
        elif selected_option.get() == "target":
            if target_n != 1:
                # Use the snapped pixel coordinates for drawing the circle
                target = canvas.create_oval(snapped_x-5, snapped_y-5, snapped_x+5, snapped_y+5, fill="blue", tags="target")  # Targets blue
                canvas.lift(target)
                target_n = 1
                # Store the grid indices for the target point
                target_point = [grid_y, grid_x]
                # print(test_grid.grid[grid_y][grid_x])
                # Update Target info label
                lat, lon = current_map.canvas_to_latlon(target_point[0], target_point[1])
                target_info_label.config(text=f"Target: [{lat:.3f}, {lon:.3f}]")

def show_depth(event):
    current_map.depth_loc(event.x, event.y)
# =========================
# EVENT BINDINGS
# =========================
# Ensure this is after all relevant definitions
def update_hover_info(event):
    """
    Updates a label with the grid indices and geographic coordinates of the mouse's current position.
    """
    global test_grid, current_map

    if 'test_grid' in globals() and test_grid is not None:
        grid_size = test_grid.cell_size

        # Snap the pixel coordinates to the nearest grid point
        snapped_x = round(event.x / grid_size)
        snapped_y = round(event.y / grid_size)

        # Get geographic coordinates if map is loaded
        if current_map is not None and hasattr(current_map, "canvas_to_latlon"):
            lat, lon = current_map.canvas_to_latlon(snapped_y * grid_size, snapped_x * grid_size)
            coord_label.config(text=f"Grid Position: ({snapped_x}, {snapped_y}) | [{lat:.3f}, {lon:.3f}]")
        else:
            coord_label.config(text="Grid Position: (x, y) | [lat, lon]")

        # Draw a small rectangle to visualize the snapped position
        canvas.delete("hover_rect")
        x1 = snapped_x * grid_size - grid_size / 2
        y1 = snapped_y * grid_size - grid_size / 2
        x2 = x1 + grid_size
        y2 = y1 + grid_size
        canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=2, tags="hover_rect")

canvas.bind("<Button-1>", handle_click)
canvas.bind("<Button-3>", show_depth)
canvas.bind("<Motion>", update_hover_info)

# =========================
# SIM MENU (SIDEBAR) BUTTONS
# =========================
# All sidebar buttons grouped together for clarity

file_button = tk.Button(
    sim_menu,
    text="Open File", 
    command=select_file,
    bg = "#333333",
    fg="white",
    width=15,
    height=1,  # Thinner button
    font=("Arial", 16),
    relief="raised"
)
start_btn = tk.Button(
    sim_menu,
    text="▶ Start",  # Add play symbol
    command=on_start_click,
    bg="green",
    fg="white",
    width=15,
    height=1,  # Thinner button
    font=("Arial", 16)
)
reset_btn = tk.Button(
    sim_menu,
    text="Reset",
    bg="#F70C03",
    fg="white",
    width=15,
    height=1,  # Thinner button
    font=("Arial", 16),
    relief="raised",
    command=lambda: reset_simulation()
)
Spawn_Attacker_btn = tk.Button(
    sim_menu,
    text="Spawn Attacker",
    bg="#A70202",
    fg="white",
    width=15,
    height=1,  # Thinner button
    font=("Arial", 16),
    relief="raised",
    command=show_spawn_panel_attacker
)
Spawn_Defender_btn = tk.Button(
    sim_menu,
    text="Spawn Defender",
    bg="#2803AD",
    fg="white",
    width=15,
    height=1,  # Thinner button
    font=("Arial", 16),
    relief="raised",
    command=show_spawn_panel_defender
)
exit_btn = tk.Button(
    sim_menu,
    text="Exit",
    bg="#333333",
    fg="white",
    width=15,
    height=1,  # Thinner button
    font=("Arial", 16),
    relief="raised",
    command=root.destroy
)

# Pack all sidebar buttons together
file_button.pack(side="top", pady=10)
tk.Label(sim_menu, text="", height=1).pack(side="top")  # Spacer between file button and start/reset buttons
start_btn.pack(side="top", pady=5)
reset_btn.pack(side="top", pady=5)
tk.Label(sim_menu, text="", height=2).pack(side="top")  # Spacer between reset and attacker/defender buttons
Spawn_Attacker_btn.pack(side="top", pady=5)
Spawn_Defender_btn.pack(side="top", pady=5)
exit_btn.pack(side="bottom", pady=10)

# =========================
# ATTACKER OVERLAY SECTION
# =========================
# Attacker overlay panel and buttons grouped together

spawn_uuv_radio = tk.Radiobutton(
    overlay_panel_attacker,
    text="Spawn UUV",
    variable=selected_option,
    value="uuv",
    bg="#333333",
    fg="white",
    selectcolor="#333333",
    width=15,
    height=1,  # Thinner button
    font=("Arial", 16),
    relief="raised"
    # Remove indicatoron=0 to restore radio button functionality
)
exit_overlay_btn_attacker = tk.Button(
    overlay_panel_attacker,
    text="Back",
    bg="#F70C03",
    fg="white",
    width=15,
    height=1,
    font=("Arial", 16),
    relief="raised",
    command=lambda: overlay_panel_attacker.place_forget()
)
spawn_uuv_radio.pack(side="top", pady=10)
exit_overlay_btn_attacker.pack(side="bottom", pady=5)

# =========================
# DEFENDER OVERLAY SECTION
# =========================
# Defender overlay panel and buttons grouped together

spawn_target_radio = tk.Radiobutton(
    overlay_panel_defender,
    text="Spawn Target",
    variable=selected_option,
    value="target",
    bg="#333333",
    fg="white",
    selectcolor="#333333",
    width=15,
    height=1,
    font=("Arial", 16),
    relief="raised"
    # Remove indicatoron=0 to restore radio button functionality
)
exit_overlay_btn_defender = tk.Button(
    overlay_panel_defender,
    text="Back",
    bg="#F70C03",
    fg="white",
    width=15,
    height=1,
    font=("Arial", 16),
    relief="raised",
    command=lambda: overlay_panel_defender.place_forget()
)
spawn_target_radio.pack(side="top", pady=10)
exit_overlay_btn_defender.pack(side="bottom", pady=10)

# Add a space between file button and radio buttons
tk.Label(sim_menu, text="", height=2).pack(side="top")

# setup the map to be drawn
# shape_path = "C:/Users/gtcdu/Downloads/extractedData_harbour_arcmap (1)/zipfolder/Harbour_Depth_Area.shp"
current_map = None
def create_map(shape_path):
    """creates the current map"""
    shallow_color = (170, 201, 250)
    deep_color = (0, 0, 26)
    global current_map
    current_map = map.MapControl(shape_path=shape_path, canvas=canvas, shallow_color=shallow_color, deep_color=deep_color)
    create_grid()
    canvas.config(background="#0A7005")  # Change background to green after loading map



# setup the agent model


# reantimate the canvas to see changes(UUV-agent-based)the oragne one
def animate():
    global animation_job
    if is_running and model_test is not None:
        model_test.step()
        animation_job = root.after(50, animate)
    else:
        animation_job = None



# ----grid testing----
def create_grid():
    global test_grid
    test_grid = Grid(width=canvas_width, height=canvas_height, cells_n=50, canvas=canvas)


root.mainloop()

def main():
    print("main loop")

if __name__ == "__main__":
    main()