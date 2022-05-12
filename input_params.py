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

        self.calculate_params()

    def calculate_params(self):
        self.PIXELS_PER_MM = 2

        self.TILE_PX_WIDTH    = self.TILE_WIDTH   *self.PIXELS_PER_MM
        self.TILE_PX_HEIGHT   = self.TILE_HEIGHT  *self.PIXELS_PER_MM
        self.GROUTING_SIZE_PX = self.GROUTING_SIZE*self.PIXELS_PER_MM
        self.GROUTING_OFFSET  = int(self.GROUTING_SIZE_PX/2)

        self.symmetry = {'vertical'      :True,
                         'horizontal'    :True,
                         'right_diagonal':False,
                         'left_diagonal' :False}

    def update_params(self, TILE_WIDTH=None,
                TILE_HEIGHT=None,
                GROUTING_SIZE=None,
                rectangle_width=None,
                rectangle_height=None):

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

        self.calculate_params()

f = open("temp", "w")
