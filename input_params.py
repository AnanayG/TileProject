# Numbers are in mm
TILE_WIDTH  = 300
TILE_HEIGHT = 300

GROUTING_SIZE = 1
rectangle_width  = 5
rectangle_height = 5

# GROUTING_SIZE = 4
# rectangle_width  = 4
# rectangle_height = 9

# GROUTING_SIZE = 1
# rectangle_width  = 120
# rectangle_height = 60

PIXELS_PER_MM = 2
TILE_PX_WIDTH  = TILE_WIDTH*PIXELS_PER_MM
TILE_PX_HEIGHT = TILE_HEIGHT*PIXELS_PER_MM
GROUTING_SIZE_PX = GROUTING_SIZE*PIXELS_PER_MM
GROUTING_OFFSET = int(GROUTING_SIZE_PX/2)

f = open("temp", "w")
