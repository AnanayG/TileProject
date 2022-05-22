import numpy as np
import cv2

def crop_image(image, width=None, height=None):
    if width is None and height is None:
        return image
    if width is None:
        return image[:, 0:height]
    if height is None:
        return image[0:width][:]
    return image[0:width, 0:height]

def image_tiled(image, mode='-TILED_Repeated-', row_repeat=2,  col_repeat=2):
    # TODO: shrink image by the factor and display
    #       add zoom functionality

    width, height, depth = image.shape
    i_width  = width-1
    i_height = height-1

    big_image = np.zeros(((row_repeat*i_width)+1, (col_repeat*i_height)+1, 3), np.uint8)
    if mode=='-TILED_Repeated-':
        big_image[0*i_width:(1)*i_width  , 0*i_height:(1)*i_height  ][:] = crop_image(image, width=i_width, height=i_height)    #LU
        big_image[1*i_width:(2)*i_width+1, 0*i_height:(1)*i_height  ][:] = crop_image(image, height=i_height)                   #RU
        big_image[0*i_width:(1)*i_width  , 1*i_height:(2)*i_height+1][:] = crop_image(image, width=i_width)                     #LB
        big_image[1*i_width:(2)*i_width+1, 1*i_height:(2)*i_height+1][:] = image                                                #RB

    elif mode=='-TILED_Mirrored-':
        # doesn't factor row_repeat and col_repeat into account, right now - TODO
        horizontally_flipped_image = np.flip(image, 1)
        veritcally_flipped_image   = np.flip(image, 0)
        reflected_flipped_image    = np.flip(veritcally_flipped_image, 1)

        #the last row/column of pixels between two reflected images is common between adjacent images
        # this last row is the grouting line
        big_image[0*i_width:(1)*i_width  , 0*i_height:(1)*i_height  ][:] = crop_image(image, width=i_width, height=i_height)        #LU
        big_image[1*i_width:(2)*i_width+1, 0*i_height:(1)*i_height  ][:] = crop_image(veritcally_flipped_image, height=i_height)    #RU
        big_image[0*i_width:(1)*i_width  , 1*i_height:(2)*i_height+1][:] = crop_image(horizontally_flipped_image, width=i_width)    #LB
        big_image[1*i_width:(2)*i_width+1, 1*i_height:(2)*i_height+1][:] = reflected_flipped_image                                  #RB

    elif mode=='-TILED_Rotated_ANTI_CLK-':
        # doesn't factor row_repeat and col_repeat into account, right now - TODO
        right_upper_image   = cv2.rotate(image, cv2.cv2.ROTATE_90_CLOCKWISE)
        left_bottom_image   = cv2.rotate(image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
        right_bottom_image  = cv2.rotate(right_upper_image, cv2.cv2.ROTATE_90_CLOCKWISE)
        
        #the last row/column of pixels between two reflected images is common between adjacent images
        # this last row is the grouting line
        big_image[0*i_width:(1)*i_width  , 0*i_height:(1)*i_height  ][:] = crop_image(image, width=i_width, height=i_height)   #LU
        big_image[1*i_width:(2)*i_width+1, 0*i_height:(1)*i_height  ][:] = crop_image(right_upper_image, height=i_height)      #RU
        big_image[0*i_width:(1)*i_width  , 1*i_height:(2)*i_height+1][:] = crop_image(left_bottom_image  , width=i_width)      #LB
        big_image[1*i_width:(2)*i_width+1, 1*i_height:(2)*i_height+1][:] = right_bottom_image                                  #RB
    
    elif mode=='-TILED_Rotated_CLK-':
        # doesn't factor row_repeat and col_repeat into account, right now - TODO
        right_upper_image   = cv2.rotate(image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
        left_bottom_image   = cv2.rotate(image, cv2.cv2.ROTATE_90_CLOCKWISE)
        right_bottom_image  = cv2.rotate(right_upper_image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        #the last row/column of pixels between two reflected images is common between adjacent images
        # this last row is the grouting line
        big_image[0*i_width:(1)*i_width  , 0*i_height:(1)*i_height  ][:] = crop_image(image, width=i_width, height=i_height)   #LU
        big_image[1*i_width:(2)*i_width+1, 0*i_height:(1)*i_height  ][:] = crop_image(right_upper_image, height=i_height)      #RU
        big_image[0*i_width:(1)*i_width  , 1*i_height:(2)*i_height+1][:] = crop_image(left_bottom_image  , width=i_width)      #LB
        big_image[1*i_width:(2)*i_width+1, 1*i_height:(2)*i_height+1][:] = right_bottom_image                                  #RB
    
    return big_image