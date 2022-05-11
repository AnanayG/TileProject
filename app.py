import numpy
import PySimpleGUI as sg
from base_classes import array_to_data, Color
from generator import Grid

# sg.theme('Dark Teal')

class App:
    def __init__(self):
        self.color_picked = Color()
        self.color_picked.from_hex('#1f77b4', name='default')

        self.canvas_base_pixel_x = 20
        self.canvas_base_pixel_y = 45
        
        self.init_graphics()

    def init_graphics(self):
        self.graph = sg.Graph((500, 500), (0, 0), (450, 450),
                              key='-GRAPH-',
                              change_submits=True,
                              drag_submits=False,
                              background_color='lightblue')
        column1 = [
          [sg.Text('Tile Size', font='ANY 15')],
          [sg.Text('Length: ', size=(12,1)), sg.In(k='-TILE_LEN-', size=(10,1))],
          [sg.Text('Width: ', size=(12,1)), sg.In(k='-TILE_WIDTH-', size=(10,1))],
        ]
        # ------ Menu Definition ------ #
        menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']],
                    ['&Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                    ['&Help', '&About...'], ]

        left_pane = [
          [sg.Menu(menu_def, tearoff=True)],
          [sg.Text('Tile Size', font='ANY 15')],
          [sg.Text('Length: ', size=(12,1)), sg.In(k='-TILE_LEN-', size=(10,1))],
          [sg.Text('Width: ', size=(12,1)), sg.In(k='-TILE_WIDTH-', size=(10,1))],

          [sg.Text('Pixel Size', font='ANY 15')],
          [sg.Text('Length: ', size=(12,1)), sg.In(k='-PIXEL_LEN-', size=(10,1))],
          [sg.Text('Width: ', size=(12,1)), sg.In(k='-PIXEL_WIDTH-', size=(10,1))],

          [sg.Text('Grouting Size', font='ANY 15'), 
             sg.Slider(range=(1, 3), default_value=2,
                       orientation='h',
                       key='-GROUTING_SIZE-',
                       enable_events=True,
                       size=(15, 15)),],
          [sg.HorizontalSeparator()],
          [sg.In("", visible=False, enable_events=True, key='set_color'),
           sg.ColorChooserButton("", size=(60, 1), target='set_color', button_color=('#1f77b4', '#1f77b4'),
                                 border_width=1, key='set_color_chooser')],
          [sg.HorizontalSeparator()],
          [sg.Frame(layout=[
            [sg.CBox('Vertical Symmetry', default=True),
            sg.CBox('Horizontal Symmetry', default=True)]],
             title='Symmetry', relief=sg.RELIEF_SUNKEN, tooltip='Use these to set flags')],
          [sg.HorizontalSeparator()],
          [sg.Ok(), sg.Cancel()]]
        
        width, height = 800, 1000

        work_canvas = sg.Graph(
          canvas_size=(width, height),
          graph_bottom_left=(0, height),
          graph_top_right=(width, 0),
          key="-CANVAS-",
          change_submits=True,  # mouse click events
          background_color='lightblue',
          drag_submits=True)
        
        layout = [
          [sg.Column(left_pane), work_canvas]
        ]
        self.window = sg.Window('Application', layout, finalize=True)

        graph = self.window["-CANVAS-"]
        self.grid = Grid(self.canvas_base_pixel_x, self.canvas_base_pixel_y)
        self.base_image = self.grid.generate_grid()
        self.update_canvas(self.base_image)

    
    def event_loop(self):
        while True:
            event, values = self.window.read(timeout=0)
            if event == 'Cancel' or event == sg.WIN_CLOSED:
                break
            elif event == 'set_color':
                print("Color picked:", values[event])
                self.color_picked = Color()
                self.color_picked.from_hex(values[event], name='picked')

                self.window['set_color_chooser'].Update(button_color=(values[event], values[event]))
            elif event == '-CANVAS-':
              print(values[event])
              image = self.grid.color_pixel(self.base_image, values[event][0], values[event][1], self.color_picked)
              self.update_canvas(image)
                
    def update_canvas(self, image):
        graph = self.window["-CANVAS-"]
        data = array_to_data(image)
        graph.draw_image(data=data, location=(self.canvas_base_pixel_x, self.canvas_base_pixel_y))

    def play(self):
        self.event_loop()


if (__name__ == "__main__"):
    game = App()
    game.play()
    sg.popup('Completed running.', 'Click OK to exit the program')
    game.window.close()
