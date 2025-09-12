from agents.model import UUVModel
import map
from grid import Grid
from gui import run_gui

def main():
    run_gui(UUVModel, map, Grid)

if __name__ == "__main__":
    main()