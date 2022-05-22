import cv2
import numpy as np

from display_image import image_tiled 
from base_classes import Point, Color
from input_params import *
from pixels import *

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
        self.no_per_width  = tileParams.no_per_width
        self.no_per_height = tileParams.no_per_height
        self.pixels_grid = [[None for _ in range(self.tileParams.no_per_height)] 
                                  for _ in range(self.tileParams.no_per_width)]

        self.symmetry   = self.tileParams.symmetry
        self.update_symm(tileParams)

        self.pixel_shape = pixel_shape

    def update_symm(self, tileParams):
        self.symmetry        = tileParams.symmetry
        self.vertical_symm   = [True, False] if (self.symmetry['vertical'] is True) else [False, False]
        self.horizontal_symm = [False, True] if (self.symmetry['horizontal'] is True) else [False, False]
        self.left_diagonal   = 'left_diagonal'  if (self.symmetry['left_diagonal' ] is True) else False
        self.right_diagonal  = 'right_diagonal' if (self.symmetry['right_diagonal'] is True) else False


    def get_unit_color(self, image, width_num, height_num):
        # base_width  = width_num *self.tileParams.pixel_width_plus_grout
        # base_height = height_num*self.tileParams.pixel_height_plus_grout
        # center = Point(base_width + (self.tileParams.pixel_width_plus_grout/2), 
        #                base_height + (self.tileParams.pixel_height_plus_grout/2))
        # coordi = center.get_point()

        # # note: height and width are reversed
        # return image[coordi[1]][coordi[0]]

        pixel = self.pixels_grid[width_num][height_num]
        return (pixel.pixel_color ,pixel.grouting_color)

    def color_pixel_with_grouting(self, image, width_num, height_num, pixel_color, grouting_color=None):
        if width_num >= self.no_per_width or width_num<0:
            raise ValueError("width num outside range"+ f"no:{width_num} total:{self.no_per_width}")
        if height_num >= self.no_per_height or height_num<0:
            raise ValueError("height num outside range " + f"no:{height_num} total:{self.no_per_height}")
        
        base_width  = width_num * self.tileParams.pixel_width_plus_grout
        base_height = height_num* self.tileParams.pixel_height_plus_grout

        center = Point(base_width  + (self.tileParams.pixel_width_plus_grout/2), 
                       base_height + (self.tileParams.pixel_height_plus_grout/2))

        if grouting_color is None:
            grouting_color = self.tileParams.GROUTING_COLOR
        pixel = self.pixel_shape(center_point=center,
                                 pixel_color=pixel_color, 
                                 grouting_color=grouting_color, 
                                 pixel_width_plus_grout =self.tileParams.pixel_width_plus_grout,
                                 pixel_height_plus_grout=self.tileParams.pixel_height_plus_grout)
        pixel.draw_grouting(image)
        pixel.draw_pixel(image, self.tileParams)
        self.pixels_grid[width_num][height_num] = pixel

    def color_pixel_and_symmetrize(self, image, width_num, height_num, pixel_color, grouting_color=None):
        set_ = {(width_num, height_num)}
        self.get_reflected_pixel_list(set_, width_num, height_num)
        for element in set_:
            self.color_pixel_with_grouting(image, element[0], element[1], pixel_color, grouting_color)

    def get_reflected_pixel_list(self, set_, width_num, height_num):
        """
        this updates the set_ with all the (x,y) after reflecting (width_num,height_num) through all the symmetries 
        """
        if self.symmetry is None:
            return
        for symm_rule in [self.vertical_symm,  self.horizontal_symm, self.left_diagonal, self.right_diagonal]:
            if symm_rule is [False, False] or symm_rule is False:
                continue

            if type(symm_rule) is str:
                width_num_reflected  = (self.no_per_height-1-height_num) if symm_rule == 'right_diagonal' else height_num
                height_num_reflected = (self.no_per_width -1- width_num) if symm_rule == 'right_diagonal' else width_num
            else:
                width_num_reflected  = (self.no_per_width -1- width_num) if symm_rule[0] is True else width_num
                height_num_reflected = (self.no_per_height-1-height_num) if symm_rule[1] is True else height_num

            #if this reflected pixel is already present in set_, do not process furthur
            if (width_num_reflected, height_num_reflected) in set_:
                continue
            set_.add((width_num_reflected, height_num_reflected))
            self.get_reflected_pixel_list(set_, width_num_reflected, height_num_reflected)

    def techniqueBlend(self, image):
        for j in range(self.no_per_width):
            for i in range(self.no_per_height):
                color_rand = np.random.choice(self.tileParams.PIXEL_COLORS, p = self.tileParams.PIXEL_COLORS_p)
                self.color_pixel_and_symmetrize(image,j,i,color_rand)

    def recolorGrouting(self, image, grouting_color):
        for j in range(self.no_per_width):
            for i in range(self.no_per_height):
                pixel_color, old_grouting_color = self.get_unit_color(image, j,i)

                # PERFORMANCE: this calculated the reflected units for each unit
                #  which can perhaps be avoided if you are doing for all rectangles
                self.color_pixel_and_symmetrize(image, width_num=j, height_num=i, 
                                    pixel_color=pixel_color, grouting_color=grouting_color)
        return image

    def swapColors(self, image, old_color, new_color):
        for j in range(self.no_per_width):
            for i in range(self.no_per_height):
                pixel_color, grouting_color = self.get_unit_color(image, j,i)

                if pixel_color.compare(old_color) is True:
                    # PERFORMANCE: this calculated the reflected units for each unit
                    #  which can perhaps be avoided if you are doing for all rectangles
                    self.color_pixel_and_symmetrize(image, width_num=j, height_num=i, 
                                        pixel_color=new_color, grouting_color=grouting_color)
        return image

class Grid:
    def __init__(self, tileParams, base_pixel_x, base_pixel_y) -> None:
        self.tileParams = tileParams
        self.base_pixel_x = base_pixel_x
        self.base_pixel_y = base_pixel_y
    
    def generate_grid(self):
        self.rect = RectanglularGrid(tileParams  = self.tileParams,
                                     pixel_shape = RectangularPixel)


        #blank image
        image = np.zeros((self.tileParams.NEW_TILE_PX_HEIGHT+1, self.tileParams.NEW_TILE_PX_WIDTH+1, 3), 
                                                        np.uint8) # height, width order is reversed
        
        #this creates blend pattern
        self.rect.techniqueBlend(image)

        #this colorises a random pixel
        num_width  = np.random.randint(self.rect.no_per_width)
        num_height = np.random.randint(self.rect.no_per_height)
        self.rect.color_pixel_and_symmetrize(image, num_width, num_height, pixel_color=self.tileParams.new_color)

        self.image = image

    def update_tiled_image(self, image, mode="-TILED_Repeated-"):
        self.tiled_image = image_tiled(image, mode=mode)

    def convert_pixel_coordinates_to_unit_coordinates(self, pixel_x, pixel_y):
        pixel_x = pixel_x - self.base_pixel_x
        pixel_y = pixel_y - self.base_pixel_y

        if (pixel_x >= self.tileParams.NEW_TILE_PX_WIDTH or pixel_x < 0):
            return (None, None)
        if (pixel_y >= self.tileParams.NEW_TILE_PX_HEIGHT or pixel_y < 0):
            return (None, None)
        
        x = pixel_x//self.tileParams.pixel_width_plus_grout
        y = pixel_y//self.tileParams.pixel_height_plus_grout

        return (x,y)

    def update_symm(self, tileParams):
        self.rect.update_symm(tileParams)
    
    def color_pixel(self, image, pixel_x, pixel_y, new_color):
        x,y = self.convert_pixel_coordinates_to_unit_coordinates(pixel_x, pixel_y)
        if x is None or y is None:
            return image
        
        self.rect.color_pixel_and_symmetrize(image, x,y, 
                    pixel_color=new_color, grouting_color=self.tileParams.GROUTING_COLOR)
        self.image = image

    def change_grouting_color(self, new_color):
        self.rect.pixel_shape.grouting_color = new_color
        newImage = self.rect.recolorGrouting(self.image, new_color)
        self.image = newImage
        self.tileParams.GROUTING_COLOR = new_color

    def get_pixel_color(self, pixel_x, pixel_y):
        x,y = self.convert_pixel_coordinates_to_unit_coordinates(pixel_x, pixel_y)
        if x is None or y is None:
            return None, None
        
        return self.rect.get_unit_color(self.image, x,y)

    def swapColors(self, old_color, new_color):
        newImage = self.rect.swapColors(self.image, old_color, new_color)
        self.image = newImage

    def save(self, filename='image.png'):
        image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(filename, image_rgb)

    def save_tiled_view(self, filename='image.png'):
        image_rgb = cv2.cvtColor(self.tiled_image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(filename, image_rgb)

if __name__ == "__main__":
    grid = Grid()
    grid.generate_grid()