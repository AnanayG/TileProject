from dataclasses import dataclass

@dataclass
class Color():
    b: int
    g: int
    r: int
    name: str

    def get_color(self):
        return (self.r, self.g, self.b)


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