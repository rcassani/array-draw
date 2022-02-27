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
    This class generate 2D or 3D visualizations for arrays:
                    ________
    1D array:     /__/__/__/|    OR    __ __ __ 
                 |__|__|__|/          |__|__|__|

                  [1, 3, 1]           [1, 3, 0]                          
                 __ 
               /__/|             __ 
              |__|/|            |__|  
              |__|/|      OR    |__|
              |__|/|            |__|
              |__|/             |__| 

            [4, 1, 1]         [4, 1, 0]                          

                  ________      _________        /|
    2D array:    |__|__|__|    /__/__/__/      /|/|  
                 |__|__|__|   /__/__/__/      |/|/| 
                 |__|__|__|                   |/|/|
                 |__|__|__|                   |/|/
                                              |/

                 [4, 3, 0]    [0, 3, 2]     [4, 0, 2]                          
                                              
                    _________
    3D array:      /__/__/__/|
                 /__/__/__/|/|
                |__|__|__|/|/| 
                |__|__|__|/|/| 
                |__|__|__|/|/
                |__|__|__|/                                                                            
            
                 [4, 3, 2]

    """
    
    def __init__(self, shape, legends=None, cube_size=30, line_size=None, cube_color='#FF0000', line_color='#000000', theta=45, projection=0.5):
        """
        Constructor method. 
        
        Arguments:
            shape:        Height, Width, Depth
            legends:      text
            cube_size:    Size of the face square
            line_size:    Width for the line (Default = cube_size // 10)
            cube_color:   Colors are given as #RRGGBB
                          1 color: For front
                              A brighter version is computed for the top (roof)
                              A darker version is computed for the side
                          3 colors: For front, top and side
                          Three 2D arrays with the color for each square tile in
                          Face, Roof, Side  [[HxW], [WxD], [HxD]]                        
            line_color:   1 color 
            theta :       Angle for depth axis in degrees [0 - 90] (Default = 45) 
            projection:   Scale for the depth units (Default = 0.5)                        
        """
#TODO Validate shape        
        # Must be [x, y, z], always 3 elements, or numpy array
        # There should be at least two dimensions
        # As such "vector" arrays need to be defined in 2D
        self.shape = shape
#TODO Validate legends
        # Empty list or 3 list (with potential empty elements)
        self.legends = legends      
        
        # Size of elements
        self.cube_size = cube_size
        if line_size is None:
            line_size = self.cube_size // 10
        self.line_size = line_size       
        
        # Projection parameters 
        self.theta = np.radians(theta)
        self.x_proj = projection * np.cos(self.theta)
        self.y_proj = projection * np.sin(self.theta)

        # Colors
        self.cube_color = self.validate_color(cube_color)
        self.line_color = line_color
           
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
        face_x_origin = self.cube_size + x_offset
        face_y_origin = self.cube_size + (self.shape[2] * self.y_proj * self.cube_size) + y_offset
        for i_height in range(self.shape[0]):
            for i_width in range(self.shape[1]):
                if type(self.cube_color[0]) is np.ndarray:
                    face_color = self.cube_color[0][i_height, i_width]    
                else:
                    face_color = self.cube_color[0] 
                svg_list.append(self.svg_face_tile(face_x_origin + (i_width  * self.cube_size), 
                                                   face_y_origin + (i_height * self.cube_size), 
                                                   self.cube_size,
                                                   face_color,                                                  
                                                   self.line_color,
                                                   self.line_size))
        # ========== Make roof tiles ==========
        roof_x_origin = self.cube_size + x_offset
        roof_y_origin = self.cube_size + (self.shape[2] * self.y_proj * self.cube_size) + y_offset
        for i_width in range(self.shape[1]):
            for i_depth in range(self.shape[2]):
                if type(self.cube_color[1]) is np.ndarray:
                    roof_color = self.cube_color[1][i_width, i_depth]    
                else:
                    roof_color = self.cube_color[1] 
                svg_list.append(self.svg_roof_tile(roof_x_origin + (i_width  * self.cube_size) + (i_depth * self.cube_size * self.x_proj), 
                                                   roof_y_origin - (i_depth * self.cube_size * self.y_proj), 
                                                   self.cube_size,
                                                   self.cube_size * self.x_proj,
                                                   self.cube_size * self.y_proj,
                                                   roof_color,                                                  
                                                   self.line_color,
                                                   self.line_size))                
        # ========== Make side tiles ==========        
        side_x_origin = self.cube_size + (self.cube_size * (self.shape[1] - 1)) + x_offset
        side_y_origin = self.cube_size + (self.shape[2] * self.y_proj * self.cube_size) + y_offset
        for i_height in range(self.shape[0]):
            for i_depth in range(self.shape[2]):
                if type(self.cube_color[2]) is np.ndarray:
                    side_color = self.cube_color[2][i_height, i_depth]    
                else:
                    side_color = self.cube_color[2]   
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
        # Draws the face (F) tile for a cube with its origin at '*' (upper left front corner)
        #   .----.
        #  /  R /|
        # *----. |
        # |  F |S.
        # |    |/
        # .----.        
        svg_str = '<rect x="{0}" y="{1}" width="{2}" height="{2}" fill="{3}" stroke="{4}" stroke-width="{5}" stroke-linejoin="round"/>'.format(x, y, size, fill_color, line_color, line_size)
        return svg_str
    
    def svg_roof_tile(self, x, y, size, x_proj, y_proj, fill_color='red', line_color='black', line_size=1):              
        # Draws the roof (R) tile for a cube with its origin at '*' (upper left front corner)
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
        # Draws the side (S) tile for a cube with its origin at '*' (upper left front corner)
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
  
    def validate_color(self, color_input):
        cube_color = []
        # Color is just one #RRGGBB string
        if type(color_input) is str:
            # Face color
            cube_color.append(color_input)  # face color
            # Roof color
            cube_color.append(self.rgba_to_hexstr(self.interpolate_color(self.hexstr_to_rgb(color_input),
                                                                         self.hexstr_to_rgb('#FFFFFF'),
                                                                         0.5)))
            cube_color.append(self.rgba_to_hexstr(self.interpolate_color(self.hexstr_to_rgb(color_input),
                                                                         self.hexstr_to_rgb('#000000'),
                                                                         0.5)))
        # Color is list with 3 elements, either:
        #    3 #RRGGBB string, or
        #    3 np.ndarrays of the sizes [HxW], [WxD], [HxD] (Face, Roof, Side)
        if len(color_input) == 3:
            cube_color = color_input       
        return cube_color              
        
    def hexstr_to_rgb(self, hexstr):
        # #FFFFFF   -> [255, 255, 255] 
        rgba = np.zeros(3)
        if len(hexstr) != 7:
            print('Color must be specified as #RRGGBB')
            return
        hexstr = hexstr[1:]
        for ix in range(len(rgba)):
            rgba[ix] = int('0x' + hexstr[2*ix : 2*(ix+1)], 16)
        return rgba
    
    def rgba_to_hexstr(self, rgba):
        # [255, 255, 255]      -> #FFFFFF
        hexstr = ''
        if len(rgba) != 3:
            print('Color must be specified as #RRGGBB')
            return
        for ix in range(len(rgba)):
            hexstr = hexstr +  "{:02x}".format(int(rgba[ix])).upper()
        hexstr = '#' + hexstr
        return hexstr
    
    def interpolate_color(self, rgb1, rgb2, step):
        # Linear interpolation between 2 colors, from color1 to color 2
        # step = 0 -> color1
        # step = 1 -> color2
        rgb = (rgb2 - rgb1) * step + rgb1       
        return rgb
    
    
if __name__== "__main__":
    # Dimensions (rows, cols, pages) 
    array_draw = ArrayDraw([4, 3, 2], cube_size=30)
    filename = './cube_testo.svg'
    array_draw.save_svg(filename)
    webbrowser.open(filename)
        
