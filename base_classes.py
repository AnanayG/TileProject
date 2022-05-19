from dataclasses import dataclass
from PIL import Image
from io import BytesIO

@dataclass
class Color():
    b: int
    g: int
    r: int
    name: str

    def __init__(self, b=None, g=None, r=None, hexcode=None, name=None):
        if hexcode is not None:
            self.from_hex(hexcode=hexcode, name=name)
        else:
            self.r = r if r is not None else 0
            self.b = b if b is not None else 0
            self.g = g if g is not None else 0
            self.name = name

    def get_color(self):
        return (int(self.r), int(self.g), int(self.b))
    
    def from_hex(self, hexcode, name=None):
        #format: #400040
        if len(hexcode)!=7:
            return False
        hexcode = hexcode[1:]
        self.r = int(hexcode[0:2],16)
        self.g = int(hexcode[2:4],16)
        self.b = int(hexcode[4:],16)
        self.name = 'picked' if name is None else name
        # print(self.name, self.r, self.g, self.b)

    def compare(self, other):
        if other is None:
            return False
        if other.r != self.r or \
            self.g != other.g or \
                self.b != other.b:
            return False
        return True

    def get_hex(self):
        hex_code = '#{0:x}{1:x}{2:x}'.format(self.r, self.g, self.b)
        return hex_code

@dataclass
class Point():
    x: int
    y: int

    def get_point(self):
        return (int(self.x), int(self.y))

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

def convert_to_int(var):
    try:
        var=int(var)
    except ValueError:
        var=None
    return var