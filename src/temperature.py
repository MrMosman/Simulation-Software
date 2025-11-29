# --- Project Information ---
# Project: UUV Simulation Framework
# Version: 1.0.0
# Date: November 2025
# 
# --- Authors and Contributors ---
# Primary:
# - Gunner Cook-Dumas (SCRUM Manager, Backend, Agent, Model, and GA Stucture)
# - Justin Mosman (developer)
# - Michael Cardinal (developer)
# 
# Secondary:
# - Lauren Milne (SCRUM Product Owner)
# 
# --- Reviewers/Bosses ---
# - Prof. Lance Fiondella, ECE, University of Massachusetts Dartmouth
# - Prof. Hang Dinh, CIS, Indiana University South Bend

from shapely.geometry import Point
from scipy.spatial import distance

class Temperature:
    def __init__(self):
        # six temp points with coordinates, top temp, and bottom temp
        self.temp_points = [
            {"coordinates": (12, 1), "top_temp": 6.6, "bottom_temp": 12.8},
            {"coordinates": (7, 14), "top_temp": 7.3, "bottom_temp": 7.4},
            {"coordinates": (12, 22), "top_temp": 9.8, "bottom_temp": 11}, #Data from six buoys in harbor, buoy points are locked in as grid coords
            {"coordinates": (9, 29), "top_temp": 10.7, "bottom_temp": 10.9}, #Closest buoy to agent is used for temp data
            {"coordinates": (14, 23), "top_temp": 9.5, "bottom_temp": 12.8},
            {"coordinates": (15, 15), "top_temp": 8.5, "bottom_temp": 11.6},
        ] 
        '''ACTUAL NOTES'''
        # As of right now temp points are hard coded and synced with grid points, not the shape file


    def find_nearest_point(self, agent_position):
        """Find the nearest temp point to the agent's position."""
        agent_point = Point(agent_position)
        nearest_point = None
        min_distance = float("inf")

        for temp_point in self.temp_points:
            point = Point(temp_point["coordinates"])
            dist = distance.euclidean(agent_point.coords[0], point.coords[0])
            if dist < min_distance:
                min_distance = dist
                nearest_point = temp_point

        return nearest_point