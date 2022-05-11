from io import BytesIO
from PIL import Image
import numpy as np
import PySimpleGUI as sg

from generator import Grid

def array_to_data(array):
    im = Image.fromarray(array)
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data

font = ("Courier New", 11)
sg.theme("DarkBlue3")
sg.set_options(font=font)

grid = Grid(0, 0)
array = grid.generate_grid()()
data = array_to_data(array)

width, height = 1000, 1000

layout = [[sg.Graph(
    canvas_size=(width, height),
    graph_bottom_left=(0, 0),
    graph_top_right=(width, height),
    key="-GRAPH-",
    change_submits=True,  # mouse click events
    background_color='lightblue',
    drag_submits=True), ],]
window = sg.Window("draw rect on image", layout, finalize=True)
graph = window["-GRAPH-"]
graph.draw_image(data=data, location=(0, height))

while True:

    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
    print(event, values)

window.close()