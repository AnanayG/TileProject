from base_classes import Color

class TileParams:
    def __init__(self):
        # Numbers are in mm
        self.TILE_WIDTH  = 300
        self.TILE_HEIGHT = 300
        self.GROUTING_SIZE = 1

        self.rectangle_width  = 5
        self.rectangle_height = 5

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

    def update_params(self, TILE_WIDTH=None,
                TILE_HEIGHT=None,
                GROUTING_SIZE=None,
                rectangle_width=None,
                rectangle_height=None,
                vertical_symm=None,
                horizontal_symm=None):

        ##TODO: add support for no_of_pixel (_per_side)
        
        ## tile_size = no_of_pixel * (pixel_unit_size + grouting_size)
        # tile_size=300, pixel_unit_size=2, grouting_size=1 so no_of_pixel=?
        # tile_size=300, pixel_unit_size=2, no_of_pixel=39  so grouting_size=?

        if TILE_WIDTH is not None:
            self.TILE_WIDTH  = TILE_WIDTH
        if TILE_HEIGHT is not None:
            self.TILE_HEIGHT     = TILE_HEIGHT
        if GROUTING_SIZE is not None:
            self.GROUTING_SIZE   = GROUTING_SIZE
        if rectangle_width is not None:
            self.rectangle_width  = rectangle_width
        if rectangle_height is not None:
            self.rectangle_height = rectangle_height

        if vertical_symm is not None:
            self.symmetry['vertical'] = vertical_symm
        if horizontal_symm is not None:
            self.symmetry['horizontal'] = horizontal_symm
        self.calculate_params()

f = open("temp", "w")
