import cv2 as cv
import numpy as np

class App:
    def __init__(self):
        cv.namedWindow('window0')

    def run(self):
        key = ''
        while key != 'q':
            k = cv.waitKey(0)
            key = chr(k)
            print(k, key)

        cv.destroyAllWindows()

if __name__ == '__main__':
    App().run()