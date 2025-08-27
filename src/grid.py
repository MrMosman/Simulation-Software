
import math
import tkinter as tk
from cell import Cell

class Grid:

    def __init__(self, width, height, cells_n, canvas):
        self.width = width
        self.height = height
        self.cells_n = cells_n
        self.canvas = canvas
        self.img_tk = None
        self.row_space = self.get_cell_spacing(self.width)  #rows invole width
        self.col_space = self.get_cell_spacing(self.height) #cols invole hieght
        print(self.row_space)
        print(self.col_space)
        self.draw_test_grid()

    def get_cell_spacing(self, length):
        width = 1
        total_obj_width = self.cells_n * width
        remaining_space = length - total_obj_width
        num_of_spaces = self.cells_n - 1
        individual_spaces = remaining_space // num_of_spaces
        return individual_spaces
    
    def draw_test_grid(self):
        pos_x = 0
        pos_y = 0
        radius = 1
        for row in range(self.cells_n): # iterate down the screen
            for col in range(self.cells_n): # iterate across the screen
                ovrlap_obj = self.canvas.find_overlapping(pos_x, pos_y, pos_x, pos_y)
                target_ojb = self.canvas.find_withtag("map")
                for id in ovrlap_obj:
                    if id in target_ojb:
                        self.canvas.create_oval(pos_x-radius, pos_y-radius, pos_x+radius, pos_y+radius, fill='white', tags='cell')
                pos_x += self.col_space       
            pos_y += self.row_space
            pos_x = 0
        





        
