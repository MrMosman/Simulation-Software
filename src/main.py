# --- Project Information ---
# Project: UUV Simulation Framework
# Version: 1.0.0
# Date: November 2025
# 
# --- Authors and Contributors ---
# Primary:
# - Gunner Cook-Dumas (SCRUM Manager, Backend, Agent, Model, and GA Stucture)
# - [Contributor 1 Full Name] (Role/Primary Contribution)
# - [Contributor 2 Full Name] (Role/Primary Contribution)
# 
# Secondary:
# - [Name] (Role/Affiliation - e.g., Algorithm Advisor)
# 
# --- Reviewers/Bosses ---
# - Prof. Lance Fiondella, ECE, University of Massachusetts Dartmouth
# - [Prof. Full Name], [Department], [Institution]

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