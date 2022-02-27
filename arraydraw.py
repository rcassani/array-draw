#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Raymundo Cassani 2022

This file defines the ArrayDraw class which generates as SVG file with 
the visualizations for 1D, 2D and 3D arrays

Methods:
    __init__()
    

'''

import numpy as np
import webbrowser

class ArrayDraw:
    """
    This class represents the cabinet projection for a 3D array
    """
    
    def __init__(self, shape, legends=None, cube_size=10, line_size=None, theta=45, projection=0.5, cube_color='red', line_color='black'):
        """
        Constructor method. 
        
        Arguments:
            shape:     Height, Width, Depth
            legends:   text
            color:     text
            cube_size:  text
            line_size:
            cube_color:
            line_color: 
            theta : Angle in degrees (Default = 45)
            projection: Length of the backwards segment (in relationship to square side)
                         
        """
#TODO Validate shape        
        # Must be [x, y, z], always 3 elements, or numpy array
        # There should be at least two dimensions
        # As such "vector" arrays need to be defined in 2D
        self.shape = shape
#TODO Validate legends
        # Empty list or 3 list (with potential empty elements)
        self.legends = legends
#TODO Validate color
     
#TODO Add color shade (mixing with white and black)
#TODO Reshape color         
        self.cube_color = cube_color
        self.line_color = line_color
        self.cube_size = cube_size
        if line_size is None:
            line_size = self.cube_size // 10
        self.line_size = line_size       
        self.theta = np.radians(theta)
        self.x_proj = projection * np.cos(self.theta)
        self.y_proj = projection * np.sin(self.theta)
    
    def get_draw_size(self):       
        width  = ((self.shape[1] * self.cube_size) +
                  (self.shape[2] * self.cube_size * self.x_proj)) 
        height = ((self.shape[0] * self.cube_size) +
                  (self.shape[2] * self.cube_size * self.y_proj))
        return width, height 
           
    def save_svg(self, filename):        
        svg_list = self.make_svg()    
        # Write SVG file to a file
        f = open(filename,'w')
        for svg_element in svg_list:
            f.write(svg_element + '\n')
        f.close()
        
#TODO Validate filename     
        #svgstr = self.make_svg()    
        return 
    
    def make_svg(self):              
        # Minimum size to show the array (with margins)
        width, height = self.get_draw_size()
        self.cube_width  = width  + (self.cube_size * 2)
        self.cube_height = height + (self.cube_size * 2)
        
        # SVG start tag
        viewbox_str = 'viewBox="0 0 ' + str(width) + str(height) + '"'
        self.svg_list = []
        self.svg_list.append('<svg xmlns="http://www.w3.org/2000/svg" width="100%" ' + viewbox_str + '>')
        
        # Fill, just to have an idea, this is tmp
        self.svg_list.append('<rect width="100%" height="100%" fill="green"/>')
        
        # Draw cube
        self.svg_list = self.svg_list + self.svg_array()
        # Draw labels
        self.svg_list = self.svg_list + self.svg_labels()
        
        # SVG end tag 
        self.svg_list.append('</svg>')
     
        return self.svg_list

    def svg_array(self, x_offset=0, y_offset=0):
        svg_list = []
        # ========== Make face tiles ==========
        # face_color = self.color_fill[0]
        face_color = 'red'
        face_x_origin = self.cube_size + x_offset
        face_y_origin = self.cube_size + (self.shape[2] * self.y_proj * self.cube_size) + y_offset
        for i_height in range(self.shape[0]):
            for i_width in range(self.shape[1]):
                if (i_width == 0) and (i_height == 0):
                    print('Hi')
                svg_list.append(self.svg_face_tile(face_x_origin + (i_width  * self.cube_size), 
                                                   face_y_origin + (i_height * self.cube_size), 
                                                   self.cube_size,
                                                   face_color,                                                  
                                                   self.line_color,
                                                   self.line_size))
        # ========== Make roof tiles ==========
        # roof_color = self.color_fill[1]
        roof_color = 'red'
        roof_x_origin = self.cube_size + x_offset
        roof_y_origin = self.cube_size + (self.shape[2] * self.y_proj * self.cube_size) + y_offset
        for i_width in range(self.shape[1]):
            for i_depth in range(self.shape[2]):
                svg_list.append(self.svg_roof_tile(roof_x_origin + (i_width  * self.cube_size) + (i_depth * self.cube_size * self.x_proj), 
                                                   roof_y_origin - (i_depth * self.cube_size * self.y_proj), 
                                                   self.cube_size,
                                                   self.cube_size * self.x_proj,
                                                   self.cube_size * self.y_proj,
                                                   roof_color,                                                  
                                                   self.line_color,
                                                   self.line_size))                
        # ========== Make side tiles ==========
        # side_color = self.color_fill[2]
        side_color = 'red'
        side_x_origin = self.cube_size + (self.cube_size * (self.shape[1] - 1)) + x_offset
        side_y_origin = self.cube_size + (self.shape[2] * self.y_proj * self.cube_size) + y_offset
        for i_height in range(self.shape[0]):
            for i_depth in range(self.shape[2]):
                svg_list.append(self.svg_side_tile(side_x_origin + (i_depth * self.cube_size * self.x_proj), 
                                                   side_y_origin + (i_height * self.cube_size) - (i_depth * self.cube_size * self.y_proj),
                                                   self.cube_size,
                                                   self.cube_size * self.x_proj,
                                                   self.cube_size * self.y_proj,
                                                   side_color,                                                  
                                                   self.line_color,
                                                   self.line_size))                                   
        return svg_list
        
    def svg_face_tile(self, x, y, size, fill_color='red', line_color='black', line_size=1):    
        # Draws the face (F) tile for a cube with its origin at * (upper left front corner)
        #   .----.
        #  /  R /|
        # *----. |
        # |  F |S.
        # |    |/
        # .----.        
        svg_str = '<rect x="{0}" y="{1}" width="{2}" height="{2}" fill="{3}" stroke="{4}" stroke-width="{5}" stroke-linejoin="round"/>'.format(x, y, size, fill_color, line_color, line_size)
        return svg_str
    
    def svg_roof_tile(self, x, y, size, x_proj, y_proj, fill_color='red', line_color='black', line_size=1):              
        # Draws the roof (R) tile for a cube with its origin at * (upper left front corner)
        #   .----.
        #  /  R /|
        # *----. |
        # |  F |S.
        # |    |/
        # .----.        
        x1 = x
        y1 = y
        x2 = x1 + x_proj
        y2 = y1 - y_proj
        x3 = x2 + size
        y3 = y2
        x4 = x3 - x_proj 
        y4 = y3 + y_proj
        svg_str = '<polygon points="{0}, {1} {2}, {3} {4}, {5} {6}, {7}" fill="{8}" stroke="{9}" stroke-width="{10}" stroke-linejoin="round"/>'.format(x1, y1, x2, y2, x3, y3, x4, y4, fill_color, line_color, line_size)
        return svg_str

    def svg_side_tile(self, x, y, size, x_proj, y_proj, fill_color='red', line_color='black', line_size=1):
        # Draws the side (S) tile for a cube with its origin at * (upper left front corner)
        #   .----.
        #  /  R /|
        # *----. |
        # |  F |S.
        # |    |/
        # .----.        
        x1 = x + size
        y1 = y
        x2 = x1 + x_proj
        y2 = y1 - y_proj
        x3 = x2
        y3 = y2 + size
        x4 = x3 - x_proj
        y4 = y3 + y_proj
        svg_str = '<polygon points="{0}, {1} {2}, {3} {4}, {5} {6}, {7}" fill="{8}" stroke="{9}" stroke-width="{10}" stroke-linejoin="round"/>'.format(x1, y1, x2, y2, x3, y3, x4, y4, fill_color, line_color, line_size)
        return svg_str

    def svg_labels(self):
        # Make axis labels
        return []
    
    def make_png(self):
        # SVG to PNG
        return
  
    def validate_color(self):
        # Either one str with the name of the color, shades are computed
        # If plane 
        #     A 1D array or List with 3 elements RGB
        # If cube
        #     A 1D array (3) or List with RBG elements, shades computed 
        #     A 2D array (3x3) with the colors for the planes
        #    An List with 3 3D arrays, each 3D array has the colors for each element in a plane  
        return
    
if __name__== "__main__":
    # Dimensions (rows, cols, pages) 
    array_draw = ArrayDraw([4, 3, 2], cube_size=30)
    filename = './cube_testo.svg'
    array_draw.save_svg(filename)
    webbrowser.open(filename)
        