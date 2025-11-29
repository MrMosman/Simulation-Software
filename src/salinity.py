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

class Salinity:
    def __init__(self):
        # six salinity points with coordinates, top salinity, and bottom salinity
        self.salinity_points = [
            {"coordinates": (12, 1), "top_salinity": 6.7, "bottom_salinity": 26.2},
            {"coordinates": (7, 14), "top_salinity": 28.8, "bottom_salinity": 29.1},
            {"coordinates": (12, 22), "top_salinity": 30.6, "bottom_salinity": 31.1}, #Data from six buoys in harbor, buoy points are locked in as grid coords
            {"coordinates": (9, 29), "top_salinity": 31.6, "bottom_salinity": 31.5}, #Closest buoy to agent is used for salinity data
            {"coordinates": (14, 23), "top_salinity": 28.8, "bottom_salinity": 31.7},
            {"coordinates": (15, 15), "top_salinity": 27.3, "bottom_salinity": 30},
        ] 
        '''ACTUAL NOTES'''
        # As of right now salinity points are hard coded and synced with grid points, not the shape file


    def find_nearest_point(self, agent_position):
        """Find the nearest salinity point to the agent's position."""
        agent_point = Point(agent_position)
        nearest_point = None
        min_distance = float("inf")

        for salinity_point in self.salinity_points:
            point = Point(salinity_point["coordinates"])
            dist = distance.euclidean(agent_point.coords[0], point.coords[0])
            if dist < min_distance:
                min_distance = dist
                nearest_point = salinity_point

        return nearest_point