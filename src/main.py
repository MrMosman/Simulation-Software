import tkinter as tk
from tkinter import filedialog as fd
import numpy as np
import pandas as pd
import mesa
import geopandas as gpd
from shapely.geometry import Point, shape
import os


# project imports
from agents.model import UUVModel
import map
from grid import Grid

# For navigating the project
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_PATH)


# setup intial window
root = tk.Tk()
root.title("fixing agents, adding placement, starting")
app_width = 800
app_height = 600
root.geometry(f'{app_width}x{app_height}')
root.resizable(False, False)

# frames and menus
sim_menu = tk.Frame(root, background='blue', width=200, height=app_height, relief="raised", border=5)
sim_menu.pack(side='left', padx=5, pady=5)
sim_menu.pack_propagate(False)
file_menu = tk.Frame(root, background="grey", width=app_width, height=100, relief="raised", border=5)
file_menu.pack(side='bottom', padx=5, pady=5)
canvas_frame = tk.Frame(root, background='blue', width=700, height=700, relief="raised", border=5)
canvas_frame.pack(side='top',  padx=5, pady=5)

canvas_width = 700
canvas_height = 700
canvas = tk.Canvas(background="#0A7005", master=canvas_frame, width=canvas_width, height=canvas_height)
canvas.pack()

# ---gridlabel---
coord_label = tk.Label(sim_menu, text="Grid Position: (x, y)")
coord_label.pack(side="top", pady=10)

def update_hover_info(event):
    """
    Updates a label with the grid indices of the mouse's current position.
    """
    global test_grid
    
    if 'test_grid' in globals() and test_grid is not None:
        grid_size = test_grid.cell_size
        
        # Snap the pixel coordinates to the nearest grid point
        snapped_x = round(event.x / grid_size)
        snapped_y = round(event.y / grid_size)
        
        # Update the label with the grid indices
        coord_label.config(text=f"Grid Position: ({snapped_x}, {snapped_y})")
        
        # Draw a small rectangle to visualize the snapped position
        # Clear previous hover rectangle if it exists
        canvas.delete("hover_rect")
        # Draw the new rectangle at the snapped pixel position
        x1 = snapped_x * grid_size - grid_size / 2
        y1 = snapped_y * grid_size - grid_size / 2
        x2 = x1 + grid_size
        y2 = y1 + grid_size
        
        canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=2, tags="hover_rect")
 


# ----buttton control----
# start simulation
spawn_point = []
target_point = None
def on_start_click():
    canvas.unbind("<Button-1>")
    start_btn.config(state="disabled")
    global model_test
    global spawn_point
    # print(spawn_point)
    model_test = UUVModel(n=tracker, canvas=canvas, spawns=spawn_point, targets=target_point, map=current_map, grid=test_grid.grid)
    root.after(100, animate)

#buttons start and stop
start_btn = tk.Button(sim_menu, text="Start", command=on_start_click, bg="white")
start_btn.pack(side="top")




# ----radio options----

def check_inside_map(event):
    """Get a list of items to determine if within boundries"""
    # get list of items
    overlapping_itmes = canvas.find_overlapping(event.x, event.y, event.x, event.y)

    is_inside_tag = False
    for item_id in overlapping_itmes:
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
    Handles the spawning of UUV and target points, snapping them to the grid.
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

        if selected_option.get()=="uuv":
            if tracker != 5:
                # Use the snapped pixel coordinates for drawing the circle on the canvas
                start = canvas.create_oval(snapped_x-5, snapped_y-5, snapped_x + 5, snapped_y +5, fill="green")
                canvas.lift(start)
                tracker += 1
                # Store the grid indices in the spawn_point list
                tmp_spw = [grid_y, grid_x]
                # print(test_grid.grid[grid_y][grid_x])
                spawn_point.append(tmp_spw)
        elif selected_option.get()=="target":
            if target_n != 1:
                # Use the snapped pixel coordinates for drawing the circle
                target = canvas.create_oval(snapped_x-5, snapped_y-5, snapped_x+5, snapped_y+5, fill="red")
                canvas.lift(target)
                target_n = 1
                # Store the grid indices for the target point
                target_point = [grid_y, grid_x]
                # print(test_grid.grid[grid_y][grid_x])

def show_depth(event):
    current_map.depth_loc(event.x, event.y)

canvas.bind("<Button-1>", handle_click)
canvas.bind("<Button-3>", show_depth)
canvas.bind("<Motion>", update_hover_info)

#radio buttons select
selected_option = tk.StringVar()
selected_option.set("uuv")


uuv_start_radio = tk.Radiobutton(sim_menu, text="Spawn uuv point", variable=selected_option, value="uuv")
target_radio = tk.Radiobutton(sim_menu, text="target point", variable=selected_option, value="target")
uuv_start_radio.pack()
target_radio.pack()

file_path = None
def select_file():
    """selects file-only allow shape files"""
    global file_path
    file_path = "C:/Users/gtcdu/Downloads/extractedData_harbour_arcmap (1)/zipfolder/Harbour_Depth_Area.shp"
    create_map(file_path)
    file_button.config(state="disabled")
    # file_path = fd.askopenfilename(title="Selct a shapfile",
    #                            initialdir="/", 
    #                            filetypes=[("Shape files", "*.shp")]
    #                             )
    # if file_path:
    #     print(f"Selcted file: {file_path}")
    #     create_map(file_path)
    # else:
    #     print("no file selected")

file_button = tk.Button(sim_menu, text="open file", command=select_file)
file_button.pack(side="top")
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



# setup the agent model


# reantimate the canvas to see changes(UUV-agent-based)the oragne one
def animate():
    """Animation loop that steps the model and updates the canvas."""
    # Schedule the next call to this function after 50 milliseconds
    root.after(50, animate)
    model_test.step()



# ----grid testing----
def create_grid():
    global test_grid
    test_grid = Grid(width=canvas_width, height=canvas_height, cells_n=50, canvas=canvas)


root.mainloop()

def main():
    print("main loop")

if __name__ == "__main__":
    main()