from dataclasses import dataclass
from PIL import Image
from io import BytesIO

@dataclass
class Color():
    b: int
    g: int
    r: int
    name: str

    def __init__(self, b=None, g=None, r=None, name=None):
        self.r = r
        self.b = b
        self.g = g
        self.name = name

    def get_color(self):
        return (self.r, self.g, self.b)
    
    def from_hex(self, hexcode, name=None):
        #format: #400040
        hexcode = hexcode[1:]
        self.r = int(hexcode[0:2],16)
        self.g = int(hexcode[2:4],16)
        self.b = int(hexcode[4:],16)
        self.name = 'picked' if name is None else name
        print(self.name, self.r, self.g, self.b)


@dataclass
class Point():
    x: int
    y: int

    def get_point(self):
        return (self.x, self.y)

    def __str__(self):
        return str(self.x) + ',' + str(self.y)
    
    def offset_point(self, offset=None, x_off=None, y_off=None):
        if offset is not None:
            return Point(self.x + offset, self.y + offset)
        else:
            return Point(int(self.x + x_off), int(self.y + y_off))

def array_to_data(array):
    im = Image.fromarray(array)
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data