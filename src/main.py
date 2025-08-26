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
sim_menu = tk.Frame(root, width=200, height=app_height, border=5)
sim_menu.pack(side='left', padx=5, pady=5)
sim_menu.pack_propagate(False)
file_menu = tk.Frame(root, background="#325672", width=app_width, height=100, relief="raised", border=5)
file_menu.pack(side='bottom', padx=5, pady=5)
file_menu.pack_propagate(False)
uuv_info_label = tk.Label(file_menu, text="UUVs: 0", bg="#325672", font=("Arial", 11), anchor="w", justify="left")
uuv_info_label.pack(fill="x", padx=10, pady=2)

target_info_label = tk.Label(file_menu, text="Target: None", bg="#325672", font=("Arial", 11), anchor="w", justify="left")
target_info_label.pack(fill="x", padx=10, pady=2)

mouse_info_label = tk.Label(file_menu, text="Mouse: None", bg="#325672", font=("Arial", 11), anchor="w")
mouse_info_label.pack(fill="x", padx=10, pady=2)
canvas_frame = tk.Frame(root, background='green', width=700, height=700, relief="raised", border=5)
canvas_frame.pack(side='top',  padx=5, pady=5)

canvas_width = 700
canvas_height = 700
canvas = tk.Canvas(background="#040404", master=canvas_frame, width=canvas_width, height=canvas_height)
canvas.pack()
def update_mouse_position(event):
    # Check if current_map is loaded and has necessary attributes
    if current_map is None or not hasattr(current_map, "shp"):
        mouse_info_label.config(text="Mouse: None")
        return
    lat, lon = current_map.canvas_to_latlon(event.x, event.y)
    mouse_info_label.config(text=f"Mouse: Lat: {lat:.3f}, Lon: {lon:.3f}")
canvas.bind("<Motion>", update_mouse_position)

# ----buttton control----
# start simulation
spawn_point = []
target_point = None
def on_start_click():
    canvas.unbind("<Button-1>")
    start_btn.config(state="disabled")
    start_btn.config(bg="red")  # Change button color to red
    start_btn.config(text="Running...") # Change button text to "Running"
    canvas_frame.config(bg="red")  # Changes canvas outline to red to show running
    global model_test
    global spawn_point
    model_test = UUVModel(n=tracker, canvas=canvas, spawns=spawn_point, targets=target_point, map=current_map)
    root.after(100, animate)

#buttons start and stop
start_btn = tk.Button(
    sim_menu,
    text="Start",
    command=on_start_click,
    bg="green",
    width=15,         # Number of text units wide
    height=2,         # Number of text units tall
    font=("Arial", 16) # Font size
)
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
    """handles the spawning of uuv and target points and updates info labels"""
    global spawn_point
    global tracker
    global target_n
    global target_point
    global selected_option

    is_inside_tag = check_inside_map(event=event)
    print(is_inside_tag)
    if is_inside_tag == True:
        if selected_option.get() == "uuv":
            if tracker != 5:
                start = canvas.create_oval(event.x-5, event.y-5, event.x + 5, event.y +5, fill="orange")
                canvas.lift(start)
                tracker += 1
                tmp_spw = np.array([event.x, event.y])
                spawn_point.append(tmp_spw)
                # Update UUV info label
                # Inside handle_click, after placing a UUV:
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
                target = canvas.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, fill="blue")
                canvas.lift(target)
                target_n = 1
                target_point = np.array([event.x, event.y])
                # Update Target info label
                lat, lon = current_map.canvas_to_latlon(target_point[0], target_point[1])
                target_info_label.config(text=f"Target: [{lat:.3f}, {lon:.3f}]")


canvas.bind("<Button-1>", handle_click)


#radio buttons select
selected_option = tk.StringVar()
selected_option.set("uuv")


uuv_start_radio = tk.Radiobutton(
    sim_menu,
    text="Spawn UUV",
    variable=selected_option,
    value="uuv",
    bg="#ED8208",        # Set background color to orange
    width=15,              # Match Start button width
    height=2,              # Match Start button height
    font=("Arial", 16),     # Match Start button font
    relief="raised"        # Make button appear raised
)
target_radio = tk.Radiobutton(
    sim_menu, 
    text="Place Target", 
    variable=selected_option, 
    value="target",
    bg = "#A00B0B",
    width=15,              # Match Start button width
    height=2,              # Match Start button height
    font=("Arial", 16),     # Match Start button font
    relief="raised"        # Make button appear raised
    )
uuv_start_radio.pack()
target_radio.pack()

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

file_button = tk.Button(
    sim_menu,
    text="Open File", 
    command=select_file,
    bg = "#9604F8",
    width=15,              # Match Start button width
    height=2,              # Match Start button height
    font=("Arial", 16),     # Match Start button font
    relief="raised"        # Make button appear raised
)
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



# setup the agent model


# reantimate the canvas to see changes(UUV-agent-based)the oragne one
def animate():
    """Animation loop that steps the model and updates the canvas."""
    # Schedule the next call to this function after 50 milliseconds
    root.after(50, animate)
    model_test.step()




root.mainloop()

def main():
    print("main loop")

if __name__ == "__main__":
    main()