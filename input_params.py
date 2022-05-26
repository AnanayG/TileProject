from base_classes import Color, Failure

class TileParams:
    def __init__(self):
        # Numbers are in mm
        self.TILE_WIDTH  = 300
        self.TILE_HEIGHT = 300
        self.GROUTING_SIZE = 1

        self.no_per_width     = None #will be calculated later
        self.no_per_height    = None #will be calculated later

        self.rectangle_width  = 5
        self.rectangle_height = 5
        self.mode = "pixel_size"
        
        self.add_gloss = False
        # GROUTING_SIZE = 4
        # rectangle_width  = 4
        # rectangle_height = 9

        # GROUTING_SIZE = 1
        # rectangle_width  = 120
        # rectangle_height = 60

        self.symmetry = {'vertical'      :True,
                         'horizontal'    :True,
                         'right_diagonal':False,
                         'left_diagonal' :False}

        self.init_colors()
        self.calculate_params()

    def init_colors(self):
        PIXEL_COLOR    = Color(r=0x3f, g=0x9a, b=0xbe, name='blue1')
        PIXEL_COLOR1   = Color(r=0x07, g=0x73, b=0x92, name='blue2')
        PIXEL_COLOR2   = Color(r=0xca, g=0xdb, b=0xe0, name='blue3')

        self.PIXEL_COLORS   = [PIXEL_COLOR, PIXEL_COLOR1, PIXEL_COLOR2]
        self.PIXEL_COLORS_p = [0.7,         0.2,          0.1]

        self.GROUTING_COLOR = Color(r=0x80, g=0xbf, b=0xca, name='blue4')
        self.new_color      = Color(r=0xff, g=0xff, b=0x00, name='yellow')

    def update_color(self, BLEND_MODE_COLORS=None, SOLID_BG_COLOR=None,
                        GROUTING_COLOR=None):
        if type(BLEND_MODE_COLORS) is dict:
            PIXEL_COLORS   = list()
            PIXEL_COLORS_p = list()
            sum_perc = 0
            for i in BLEND_MODE_COLORS:
                color      = BLEND_MODE_COLORS[i][f'-BLEND_COLOR{i}-']
                color_perc = BLEND_MODE_COLORS[i][f'-BLEND_COLOR{i}_PERCENT-']
                if color is None:
                    continue
                sum_perc = sum_perc + color_perc
                PIXEL_COLORS.append  (color)
                PIXEL_COLORS_p.append(color_perc/100.0)
            if sum_perc == 100:
                self.PIXEL_COLORS = PIXEL_COLORS
                self.PIXEL_COLORS_p = PIXEL_COLORS_p
            else:
                print("Sum of blend colors is not 100. Using older colors")
        elif type(SOLID_BG_COLOR) is Color:
            self.PIXEL_COLORS   = [SOLID_BG_COLOR]
            self.PIXEL_COLORS_p = [1]
            
        if GROUTING_COLOR is not None:
            self.GROUTING_COLOR = GROUTING_COLOR            

    def calculate_params(self):
        self.PIXELS_PER_MM = 2

        self.TILE_PX_WIDTH    = self.TILE_WIDTH   *self.PIXELS_PER_MM
        self.TILE_PX_HEIGHT   = self.TILE_HEIGHT  *self.PIXELS_PER_MM
        self.GROUTING_SIZE_PX = self.GROUTING_SIZE*self.PIXELS_PER_MM
        self.GROUTING_OFFSET  = int(self.GROUTING_SIZE_PX/2)

        #height, width are in mm
        (unit_width, unit_height)= self.set_unit_size()
        unit_px_width  = unit_width  * self.PIXELS_PER_MM
        unit_px_height = unit_height * self.PIXELS_PER_MM

        self.pixel_width_plus_grout  = unit_px_width  + self.GROUTING_SIZE_PX
        self.pixel_height_plus_grout = unit_px_height + self.GROUTING_SIZE_PX

        if self.mode == "pixel_size":
            self.no_per_width  = int(self.TILE_PX_WIDTH /self.pixel_width_plus_grout)
            self.no_per_height = int(self.TILE_PX_HEIGHT/self.pixel_height_plus_grout)
        
        self.NEW_TILE_PX_WIDTH  = self.no_per_width  * self.pixel_width_plus_grout
        self.NEW_TILE_PX_HEIGHT = self.no_per_height * self.pixel_height_plus_grout
        print(f"RESIZING IMAGE TO WIDTH:{self.NEW_TILE_PX_WIDTH}, \
                                  HEIGHT:{self.NEW_TILE_PX_HEIGHT}")

    def update_grouting_size(self, NEW_GROUTING_SIZE):
        # no_per_width, no_per_height is unaffected
        # pixel_height_plus_grout, pixel_width_plus_grout is also unaffected
        print(f"updating grouting size to {NEW_GROUTING_SIZE}")
        self.GROUTING_SIZE    = NEW_GROUTING_SIZE
        self.GROUTING_SIZE_PX = self.GROUTING_SIZE*self.PIXELS_PER_MM
        self.GROUTING_OFFSET  = int(self.GROUTING_SIZE_PX/2)
        if self.mode == "pixel_size":
            self.rectangle_width  = self.pixel_width_plus_grout  - self.GROUTING_SIZE
            self.rectangle_height = self.pixel_height_plus_grout - self.GROUTING_SIZE
    
    def set_unit_size(self):
        if self.rectangle_width is not None and \
            self.rectangle_height is not None:
            self.mode = "pixel_size"
            return (self.rectangle_width, self.rectangle_height)
        
        if self.no_per_width is not None and \
            self.no_per_height is not None:
            width  = int(self.TILE_WIDTH/self.no_per_width)  - self.GROUTING_SIZE
            height = int(self.TILE_WIDTH/self.no_per_height) - self.GROUTING_SIZE
            if width <0 or height<0:
                return (None, None)
            self.mode = "pixel_number"
            return (width, height)

    def update_params(self, TILE_WIDTH=None, TILE_HEIGHT=None,
                GROUTING_SIZE=None,
                rectangle_width=None, rectangle_height=None,
                num_width=None, num_height=None,
                vertical_symm=None, horizontal_symm=None,
                right_d_symm=None, left_d_symm=None):

        if TILE_WIDTH is not None:
            self.TILE_WIDTH  = TILE_WIDTH
        if TILE_HEIGHT is not None:
            self.TILE_HEIGHT     = TILE_HEIGHT
        if GROUTING_SIZE is not None:
            self.GROUTING_SIZE   = GROUTING_SIZE
        
        if num_width is not None and num_height is not None:
            self.no_per_width     = num_width
            self.no_per_height    = num_height
            self.rectangle_width  = None
            self.rectangle_height = None

        if rectangle_width is not None and rectangle_height is not None:
            self.no_per_width     = None
            self.no_per_height    = None
            self.rectangle_width  = rectangle_width
            self.rectangle_height = rectangle_height

        if vertical_symm is not None:
            self.symmetry['vertical'] = vertical_symm
        if horizontal_symm is not None:
            self.symmetry['horizontal'] = horizontal_symm
        if right_d_symm is not None:
            self.symmetry['right_diagonal'] = right_d_symm
        if left_d_symm is not None:
            self.symmetry['left_diagonal'] = left_d_symm
        
        self.calculate_params()
        return self.check_errors()
    
    def check_errors(self):
        # under diagonal symmetry, no_per_width must be same as no_per_height
        if self.symmetry['right_diagonal'] is True or \
            self.symmetry['left_diagonal'] is True:
            if self.no_per_width != self.no_per_height:
                error_msg = "unit_num_width:{0} unit_num_height:{1} must be same under diagonal symmetry. \
                    \nEnter newer values and try again!".format(self.no_per_width, self.no_per_height)
                return Failure(error_msg)

