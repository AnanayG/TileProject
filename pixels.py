from base_classes import Point, Color
import cv2
from input_params import *

class RectangularPixel():
    l_top: Point
    r_bot:  Point
    pixel_color: Color
    grouting_color: Color
    pixel_width_plus_grout: int
    pixel_height_plus_grout: int

    def __init__(self, l_top=None, r_bot=None, center_point = None,
                    pixel_color=None, 
                    grouting_color=None,
                    pixel_width_plus_grout=None,
                    pixel_height_plus_grout=None):
        self.l_top = l_top
        self.r_bot = r_bot

        self.pixel_color = pixel_color
        self.grouting_color = grouting_color
        self.pixel_width_plus_grout = pixel_width_plus_grout
        self.pixel_height_plus_grout = pixel_height_plus_grout

        if center_point is not None:
            self.init_corners(center_point=center_point)
            
    def init_corners(self, center_point):
        self.l_top = center_point.offset_point(x_off= -(self.pixel_width_plus_grout/2), y_off= -(self.pixel_height_plus_grout/2))
        self.r_bot = center_point.offset_point(x_off=  (self.pixel_width_plus_grout/2), y_off=  (self.pixel_height_plus_grout/2))

        f.write(str(self.l_top) + ' ' + str(self.r_bot) + ' ')

    def draw_grouting(self, image):
        cv2.rectangle(image, 
                self.l_top.get_point(),
                self.r_bot.get_point(),
                self.grouting_color.get_color(),
                thickness=cv2.FILLED
            )

    def draw_pixel(self, image, tileParams):
        cv2.rectangle(image, 
                    self.l_top.offset_point(offset= tileParams.GROUTING_OFFSET).get_point(), 
                    self.r_bot.offset_point(offset=-tileParams.GROUTING_OFFSET).get_point(), 
                    self.pixel_color.get_color(), 
                    thickness=cv2.FILLED
                )
