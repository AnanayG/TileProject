import cv2
import numpy as np

from display_image import image_tiled 
from base_classes import Point, Color
from input_params import *
from pixels import *

# PIXEL_COLOR    = Color(255,0,0)
PIXEL_COLOR    = Color(0x3f,0x9a,0xbe, 'blue1')
PIXEL_COLOR1   = Color(0x07,0x73,0x92, 'blue2')
PIXEL_COLOR2   = Color(0xca,0xdb,0xe0, 'blue3')

GROUTING_COLOR = Color(0x80,0xbf,0xca, 'blue4')
new_color      = Color(255,255,0, 'yellow')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--Seed", help = "Random Seed")
args = parser.parse_args()
if args.Seed:
    print("Random Seed: % s" % args.Seed)
    np.random.seed(int(args.Seed))


class RectanglularGrid():
    def __init__(self, tileParams=None, pixel_shape=None):
        self.tileParams = tileParams
        self.symmetry   = self.tileParams.symmetry

        self.vertical_symm   = [True, False] if (self.symmetry['vertical'] is True) else [False, False]
        self.horizontal_symm = [False, True] if (self.symmetry['horizontal'] is True) else [False, False]
        self.right_diagonal  = [True, True]  if (self.symmetry['right_diagonal'] is True) else [False, False]
        self.left_diagonal   = [True, True]  if (self.symmetry['left_diagonal'] is True) else [False, False]

        self.pixel_shape = pixel_shape

    def resize_image(self, width, height, tileParams):
        #height, width are in mm
        pixel_width  = width  * tileParams.PIXELS_PER_MM
        pixel_height = height * tileParams.PIXELS_PER_MM

        self.pixel_width_plus_grout  = pixel_width + tileParams.GROUTING_SIZE_PX
        self.pixel_height_plus_grout = pixel_height+ tileParams.GROUTING_SIZE_PX

        self.no_per_width  = int(tileParams.TILE_PX_WIDTH/self.pixel_width_plus_grout)
        self.no_per_height = int(tileParams.TILE_PX_HEIGHT/self.pixel_height_plus_grout)
        f.write(f'{self.no_per_width=} {self.no_per_height=}' + '\n')

        NEW_TILE_PX_WIDTH = self.no_per_width*self.pixel_width_plus_grout
        NEW_TILE_PX_HEIGHT = self.no_per_height*self.pixel_height_plus_grout
        print(f"RESIZING IMAGE TO WIDTH:{NEW_TILE_PX_WIDTH}, height:{NEW_TILE_PX_HEIGHT}")

        return (NEW_TILE_PX_WIDTH, NEW_TILE_PX_HEIGHT)

    def color_pixel_with_grouting(self, image, width_num, height_num, pixel_color, grouting_color=GROUTING_COLOR):
        if width_num >= self.no_per_width or width_num<0:
            raise ValueError("width num outside range"+ f"no:{width_num} total:{self.no_per_width}")
        if height_num >= self.no_per_height or height_num<0:
            raise ValueError("height num outside range " + f"no:{height_num} total:{self.no_per_height}")
        
        base_width  = width_num *self.pixel_width_plus_grout
        base_height = height_num*self.pixel_height_plus_grout

        center = Point(base_width + (self.pixel_width_plus_grout/2), base_height + (self.pixel_height_plus_grout/2))

        pixel = self.pixel_shape(center_point=center,
                                 pixel_color=pixel_color, 
                                 grouting_color=grouting_color, 
                                 pixel_width_plus_grout=self.pixel_width_plus_grout,
                                 pixel_height_plus_grout=self.pixel_height_plus_grout)
        pixel.draw_grouting(image)
        pixel.draw_pixel(image, self.tileParams)

    def color_pixel_and_symmetrize(self, image, width_num, height_num, pixel_color):
        set_ = {(width_num, height_num)}
        self.get_reflected_pixel_list(set_, width_num, height_num, pixel_color)
        for element in set_:
            self.color_pixel_with_grouting(image, element[0], element[1], pixel_color)

    def get_reflected_pixel_list(self, set_, width_num, height_num, pixel_color):
        """
        this updates the set_ with all the (x,y) after reflecting (width_num,height_num) through all the symmetries 
        """
        if self.symmetry is None:
            return
        for symm_rule in [self.vertical_symm,  self.horizontal_symm]:
            if symm_rule is [False, False]:
                continue

            width_num_reflected  = (self.no_per_width -1- width_num) if symm_rule[0] is True else width_num
            height_num_reflected = (self.no_per_height-1-height_num) if symm_rule[1] is True else height_num
            
            #if this reflected pixel is already present in set_, do not process furthur
            if (width_num_reflected, height_num_reflected) in set_:
                continue
            set_.add((width_num_reflected, height_num_reflected))
            self.get_reflected_pixel_list(set_, width_num_reflected, height_num_reflected, pixel_color)

    def techniqueBlend(self, image):
        for i in range(self.no_per_height):
            for j in range(self.no_per_width):
                color_rand = np.random.choice([PIXEL_COLOR, PIXEL_COLOR1, PIXEL_COLOR2], p = [0.7,0.2,0.1])
                # f.write(f'{color_rand.name=} {i} {j} \n')
                self.color_pixel_and_symmetrize(image,j,i,color_rand)

class Grid:
    def __init__(self, tileParams, base_pixel_x, base_pixel_y) -> None:
        self.tileParams = tileParams
        self.base_pixel_x = base_pixel_x
        self.base_pixel_y = base_pixel_y
    
    def generate_grid(self):
        self.rect = RectanglularGrid(tileParams  = self.tileParams,
                                     pixel_shape = RectangularPixel)

        #shortens the tile to the nearest multiple of pixels
        self.NEW_TILE_PX_WIDTH, self.NEW_TILE_PX_HEIGHT = self.rect.resize_image(self.tileParams.rectangle_width,
                                                                                 self.tileParams.rectangle_height,
                                                                                 tileParams=self.tileParams)

        #blank image
        image = np.zeros((self.NEW_TILE_PX_HEIGHT+1, self.NEW_TILE_PX_WIDTH+1, 3), np.uint8) # height, width order is reversed
        
        #this creates blend pattern
        self.rect.techniqueBlend(image)

        num_width  = np.random.randint(self.rect.no_per_width)
        num_height = np.random.randint(self.rect.no_per_height)
        self.rect.color_pixel_and_symmetrize(image, num_width, num_height, pixel_color=new_color)

        self.image = image
        return image
        cv2.imshow('Rectangular Pattern-color-changed', image)
        cv2.waitKey(0)

        big_image = image_tiled(image, mode="rotated")
        cv2.imshow('Repeated', big_image)
        cv2.waitKey(0)

        cv2.destroyAllWindows()

    def convert_pixel_coordinates_to_unit_coordinates(self, pixel_x, pixel_y):
        pixel_x = pixel_x - self.base_pixel_x
        pixel_y = pixel_y - self.base_pixel_y

        if (pixel_x > self.NEW_TILE_PX_WIDTH or pixel_x < 0):
            return (None, None)
        if (pixel_y > self.NEW_TILE_PX_HEIGHT or pixel_y < 0):
            return (None, None)
        
        x = pixel_x//self.rect.pixel_width_plus_grout
        y = pixel_y//self.rect.pixel_height_plus_grout

        return (x,y)

    def color_pixel(self, image, pixel_x, pixel_y, new_color):
        x,y = self.convert_pixel_coordinates_to_unit_coordinates(pixel_x, pixel_y)
        if x is None or y is None:
            return image
        
        self.rect.color_pixel_and_symmetrize(image, x,y, pixel_color=new_color)
        self.image = image
        return image

    def get_pixel_color(self, pixel_x, pixel_y):
        x,y = self.convert_pixel_coordinates_to_unit_coordinates(pixel_x, pixel_y)
        if x is None or y is None:
            return None
        return self.image[x,y]

if __name__ == "__main__":
    grid = Grid()
    grid.generate_grid()