import cv2 as cv
import numpy as np

BLACK = (0, 0, 0)
GRAY = (20, 20, 20)
YELLOW = (255, 0, 255)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
WHITE = (255, 255, 255)

def help():
    print('--- HELP ---')

class App:
    wins = []
    win = None
    win_id = 0
    options = dict(win_color=GRAY, obj_color=YELLOW, sel_color=BLUE)

    def __init__(self):
        cv.namedWindow('window0')
        self.shortcuts = {'h': help,
                          'i': self.inspect,
                          'w': Window,
                          'o': Object}
    
    def key(self, k):
        if k in self.shortcuts:
            self.shortcuts[k]()

    def inspect(self):
        print('--- INSPECT ---')
        print('App.wins', App.wins)
        print('App.win', App.win)

    def run(self):
        key = ''
        while key != 'q':
            key = cv.waitKey(0)

            if key >= 0:
                k = chr(key)
                if not App.win.key(k):
                    self.key(k)
                print(k, key)

        cv.destroyAllWindows()

class Window:
    obj_options = dict(pos=(20, 20), size=(100, 30), id=0)

    """Create a window."""
    def __init__(self, win=None, img=None):
        App.wins.append(self)
        App.win = self

        self.objs = []
        self.obj = None

        if img==None:
            img = np.zeros((200, 600, 3), np.uint8)
            img[:,:] = App.options['win_color']
        if win == None:
            win = 'window' + str(App.win_id)
        App.win_id += 1

        self.win = win
        self.img = img
        self.img0 = img.copy()

        cv.imshow(win, img)
    
        cv.setMouseCallback(win, self.mouse)

        self.shortcuts = {  '\t': self.select_next_obj,
                    chr(27): self.unselect_obj }

    def select_next_obj(self):
        """Select the next object, or the first in none is selected."""
        try:
            i = self.objs.index(self.obj)
        except ValueError:
            i = -1
        self.objs[i].selected = False
        i = (i+1) % len(self.objs)
        self.objs[i].selected = True
        self.obj = self.objs[i]

    def unselect_obj(self):
        if self.obj != None:
            self.obj.selected = False
            self.obj = None

    def mouse(self, event, x, y, flags, param):
        text = "mouse event {} at ({}, {}) with flags {}".format(event, x, y, flags)
        print(text)
        # cv.displayStatusBar(self.win, text, 1000)
        if event == cv.EVENT_LBUTTONDOWN:
            print(self)
            App.win = self
            self.obj = None
            for obj in self.objs:
                obj.selected = False
                if obj.is_inside(x, y):
                    obj.selected = True
                    self.obj = obj
        if event == cv.EVENT_MOUSEMOVE:
            if flags == cv.EVENT_FLAG_ALTKEY:
                self.obj.pos = x, y
        self.draw()

    def key(self, k):
        if k in self.shortcuts:
            self.shortcuts[k]()
            self.draw()
            return True

        elif self.obj != None:
            self.obj.key(k)
            self.draw()
            return True

        elif k == chr(0):  # alt, ctrl, shift
            self.upper = not self.upper
            if self.upper:
                cv.displayStatusBar(self.win, 'UPPER case', 1000)
            else:
                cv.displayStatusBar(self.win, 'LOWER case', 1000)
            return True

        return False

    def draw(self):
        self.img[:] = self.img0[:]

        for obj in self.objs:
            obj.draw()

        cv.imshow(self.win, self.img)

class Object:
    """Add an object to the current window."""
    def __init__(self, **options):
        App.win.objs.append(self)
        App.win.obj = self
        self.img = App.win.img

        self.obj_options = Window.obj_options.copy()

        d = App.win.obj_options
        d.update(options)

        self.id = d['id']
        self.pos = x, y = d['pos']
        self.size = w, h = d['size']

        self.selected = False

        d['id'] += 1
        d['pos'] = x, y + h + 5
    
    
    def key(self, k):
        pass
        
    def __str__(self):
        return 'Object {} at ({}, {})'.format(self.id, *self.pos)

    def draw(self):
        x, y = self.pos
        w, h = self.size
        cv.rectangle(self.img, (x, y, w, h), App.options['obj_color'], 1)
        if self.selected:
            cv.rectangle(self.img, (x-2, y-2, w+2, h+2), App.options['sel_color'], 2)
    
    def is_inside(self, x, y):
        x0, y0 = self.pos
        w, h = self.size
        return x0 <= x <= x0+w and y0 <= y <= y0+h

if __name__ == '__main__':
    app = App()
    win = Window()
    app.run()