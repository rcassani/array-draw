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
    
    def __init__(self, shape, cube_size=30, cube_color='#FF0000',
                              line_size=None, line_color='#000000', 
                              legends=[None, None, None], legend_size=None, 
                              title=None, title_size=None, 
                              background_color = None, text_color='#000000',
                              theta=45, projection=0.5):       
        """
        Constructor method. 
        
        Arguments:
            shape:        Height, Width, Depth
            cube_size:    Size of the face square
            cube_color:   Colors are given as #RRGGBB
                          1 color: For front
                              A brighter version is computed for the top (roof)
                              A darker version is computed for the side
                          3 colors: For front, top and side
                          Three 2D arrays with the color for each square tile in
                          Face, Roof, Side  [[HxW], [WxD], [HxD]]                        
            line_size:    Width for the line (Default = cube_size // 10)
            line_color:   1 color
            legends:      3-element list for Height, Width, Depth
                              Use empty strings '' to add space for labels 
            legend_size:   
            title:        String, use empty strings '' to add space for labels 
            title_size:   
            back_color:   Background color
            text_color:   Text color  
            theta :       Angle for depth axis in degrees [0 - 90] (Default = 45) 
            projection:   Scale for the depth units (Default = 0.5)                        
        """
        
        # Validate shape
        if len(shape) != 3:
            print('Shape must be a list of 3 elements')
            return
        nz = 0
        for element in shape:
            if element <= 0:
                nz = nz + 1
        if nz > 1:
            print('At least two dimensions must be >= 1')
            return                
        self.shape = shape
        # Validate legends
        if legends is None:
            legends = [None, None, None]
        self.legends = legends             
        # Validate title
        if title is None:
            title = ''
        self.title = title
        # Size of elements
        self.cube_size = cube_size
        if line_size is None:
            line_size = self.cube_size // 10
        self.line_size = line_size       
        if legend_size is None:
            legend_size = self.cube_size / 4
        self.legend_size = legend_size
        if title_size is None:
            title_size = self.cube_size / 2
        self.title_size = title_size       
        
        # Colors
        self.cube_color = self.validate_color(cube_color)
        self.line_color = line_color
        self.background_color = background_color
        self.text_color = text_color
        
        # Projection parameters 
        self.theta = theta
        self.projection = projection
        self.x_proj = self.projection * np.cos(np.radians(self.theta))
        self.y_proj = self.projection * np.sin(np.radians(self.theta))
           
    def get_array_size(self):       
        width  = ((self.shape[1] * self.cube_size) +
                  (self.shape[2] * self.cube_size * self.x_proj)) 
        height = ((self.shape[0] * self.cube_size) +
                  (self.shape[2] * self.cube_size * self.y_proj))
        return width, height 
    
    def get_labels_margins(self):
        margins = [0, 0, 0, 0] # [URDL]
        # Height label
        if self.legends[0] != None:
            margins[3] = 1.5 * self.legend_size        
        # Width label
        if self.legends[1] != None:
            margins[2] = 1.5 * self.legend_size
        # Title label
        if self.title != None:
            margins[0] = 1.5 * self.title_size
        return margins 
       
    def save_svg(self, filename):        
        svg_list = self.make_svg()    
        # Write SVG file to a file
        f = open(filename,'w')
        for svg_element in svg_list:
            f.write(svg_element + '\n')
        f.close()
        
        return 
    
    def make_svg(self):              
        # Minimum area to show the array
        width, height = self.get_array_size()
        # Additional space of labels [Top, Right, Bottom, Left]
        label_margins = self.get_labels_margins()
        # Additional margins [Top, Right, Bottom, Left] (One 'cube_side')
        space_margins = [self.cube_size, self.cube_size, self.cube_size, self.cube_size]        
        # Add margins
        self.cube_width  = space_margins[1] + label_margins[1] + width  + space_margins[3] + label_margins[3]       
        self.cube_height = space_margins[0] + label_margins[0] + height + space_margins[2] + label_margins[2]
        
        # Reference point (upper left corner of the area to show the array)
        x_offset = 0 + label_margins[3] + space_margins[3] 
        y_offset = 0 + label_margins[0] + space_margins[0] 
        
        # SVG start tag
        viewbox_str = 'viewBox="0 0 ' + str(self.cube_width) + ' ' + str(self.cube_height) + '"'
        self.svg_list = []
        self.svg_list.append('<svg xmlns="http://www.w3.org/2000/svg" ' + viewbox_str + '>')
        
        # Set background color
        if self.background_color is not None:               
            self.svg_list.append('<rect width="100%" height="100%" fill="{0}"/>'.format(self.background_color))
        
        # Draw cube
        self.svg_list = self.svg_list + self.svg_array(x_offset, y_offset)
        # Draw labels
        self.svg_list = self.svg_list + self.svg_labels(x_offset, y_offset)
        
        # SVG end tag 
        self.svg_list.append('</svg>')
     
        return self.svg_list

    def svg_array(self, x_offset=0, y_offset=0):
        svg_list = []
        # ========== Make face tiles ==========
        face_x_origin = x_offset
        face_y_origin = y_offset + (self.shape[2] * self.y_proj * self.cube_size)
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
        roof_x_origin = x_offset
        roof_y_origin = y_offset + (self.shape[2] * self.y_proj * self.cube_size) 
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
        side_x_origin = x_offset + (self.cube_size * (self.shape[1] - 1))
        side_y_origin = y_offset + (self.shape[2] * self.y_proj * self.cube_size)
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

    def svg_labels(self, x_offset=0, y_offset=0):
        # Add (axis) legends and title text if available
        #      TITLE
        #      .----.
        #     /    /|
        #    *----. |
        #  H |    | .
        #    |    |/ D
        #    .----.        
        #      W
        svg_list = []
        # Template for text in SVG, [x, y] is the center of the text
        template_string = ('<text x="{0}" y="{1}" transform="rotate({2},{0},{1})" ' +
                           'font-size="{3}" font-family="Arial, Helvetica, sans-serif" ' +
                           'dominant-baseline="middle" text-anchor="{4}">{5}</text>')
        # Height label
        if self.legends[0] != None:
            x = x_offset - self.legend_size
            y = y_offset + (self.shape[2] * self.y_proj * self.cube_size) + (self.shape[0] * self.cube_size) / 2
            svg_list.append(template_string.format(x, y, -90, self.legend_size, 'middle', self.legends[0]))        
        # Width label
        if self.legends[1] != None:
            x = x_offset + (self.shape[1] * self.cube_size) / 2
            y = y_offset + (self.cube_size * ((self.shape[2] * self.y_proj) + self.shape[0])) + self.legend_size
            svg_list.append(template_string.format(x, y, 0, self.legend_size, 'middle', self.legends[1]))                    
        # Depth label
        if self.legends[2] != None:
            x = x_offset + (self.shape[1] * self.cube_size) + ((self.shape[2] * self.x_proj * self.cube_size) / 2) + (self.x_proj / self.projection * self.legend_size) 
            y = y_offset + ((self.shape[2] * self.y_proj * self.cube_size) / 2) + (self.shape[0] * self.cube_size) + (self.y_proj / self.projection * self.legend_size) 
            svg_list.append(template_string.format(x, y, -self.theta, self.legend_size, 'middle', self.legends[2]))        
        # Title label
        if self.title != None:
            x = x_offset + self.cube_size * (self.shape[1] + (self.shape[2] * self.x_proj)) / 2 
            y = y_offset - self.title_size
            svg_list.append(template_string.format(x, y, 0, self.title_size, 'middle', self.title))        
        return svg_list
    
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
    # Examples 
    filename_base = './example_'
    filename_ext  = '.svg'
    i_example = 1
    # 2D array as plane
    filename = filename_base + str(i_example) + filename_ext
    i_example = i_example + 1
    array_draw = ArrayDraw([4, 3, 0])
    array_draw.save_svg(filename)
    webbrowser.open(filename)
    # 2D array as cuboid
    filename = filename_base + str(i_example) + filename_ext
    i_example = i_example + 1
    array_draw = ArrayDraw([4, 3, 1])
    array_draw.save_svg(filename)
    webbrowser.open(filename)
    # 3D array as cuboid
    filename = filename_base + str(i_example) + filename_ext
    i_example = i_example + 1
    array_draw = ArrayDraw([4, 3, 2])
    array_draw.save_svg(filename)
    webbrowser.open(filename)
    # 3D array, custom color hue, custom line color
    filename = filename_base + str(i_example) + filename_ext
    i_example = i_example + 1
    array_draw = ArrayDraw([4, 3, 2], cube_color='#304e6c', line_color='#6f6f6f')
    array_draw.save_svg(filename)
    webbrowser.open(filename)
    # 3D array, custom face, roof and side colors
    filename = filename_base + str(i_example) + filename_ext
    i_example = i_example + 1
    array_draw = ArrayDraw([4, 3, 2], cube_color=['#ff0000', '#00ff00', '#0000ff'])
    array_draw.save_svg(filename)
    webbrowser.open(filename)        
    # 3D array, custom colors for each tile in face, roof and side
    filename = filename_base + str(i_example) + filename_ext
    i_example = i_example + 1
    face_colors = np.array([['#ff0000', '#ffffff', '#ffff00'], ['#0000ff', '#0000ff', '#ff8c00'], ['#00ff00', '#ff0000', '#ffff00']])
    roof_colors = np.array([['#ffffff', '#ff8c00', '#0000ff'], ['#ff0000', '#ffff00', '#00ff00'], ['#ff8c00', '#ffffff', '#ffffff']])
    side_colors = np.array([['#00ff00', '#0000ff', '#ff0000'], ['#ffff00', '#ff0000', '#ff0000'], ['#ff0000', '#ffff00', '#ff8c00']])
    array_draw = ArrayDraw([3, 3, 3], cube_color=[face_colors, roof_colors, side_colors])
    array_draw.save_svg(filename)
    webbrowser.open(filename)    
    # 3D array, custom face, roof and side colors, plus labels and title
    filename = filename_base + str(i_example) + filename_ext
    i_example = i_example + 1
    array_draw = ArrayDraw([4, 3, 2], cube_color=['#ff0000', '#00ff00', '#0000ff'],                            
                           legends=['Frequency', 'Time', 'Channel'],
                           title='Spectrogram', 
                           background_color='#ffffff')
    array_draw.save_svg(filename)
    webbrowser.open(filename)