from agents.model import UUVModel
import map
import os
from New_gui import App

def main():
    # setup globals
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_PATH)
    app = App('simulation', (1100,600), PARENT_DIR)
     
if __name__ == "__main__":
    main()