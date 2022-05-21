import numpy as np

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
        for i in range(row_repeat):
            for j in range(col_repeat):
                big_image[i*width:(i+1)*width, j*height:(j+1)*height][:] = image
    elif mode=='-TILED_Rotated-':
        # doesn't factor row_repeat and col_repeat into account, right now - TODO
        horizontally_flipped_image = np.flip(image, 1)
        veritcally_flipped_image   = np.flip(image, 0)
        reflected_flipped_image    = np.flip(veritcally_flipped_image, 1)

        #the last row/column of pixels between two reflected images is common between adjacent images
        # this last row is the grouting line
        big_image[0*i_width:(1)*i_width, 0*i_height:(1)*i_height]  [:]   = crop_image(image, width=i_width, height=i_height)        #LU
        big_image[1*i_width:(2)*i_width+1, 0*i_height:(1)*i_height][:]   = crop_image(veritcally_flipped_image, height=i_height)    #RU
        big_image[0*i_width:(1)*i_width, 1*i_height:(2)*i_height+1][:]   = crop_image(horizontally_flipped_image, width=i_width)    #LB
        big_image[1*i_width:(2)*i_width+1, 1*i_height:(2)*i_height+1][:] = reflected_flipped_image                                  #RB

    return big_image