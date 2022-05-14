import numpy
import PySimpleGUI as sg
from base_classes import array_to_data, Color
from generator import Grid
from input_params import TileParams

# sg.theme('Dark Teal')

class App:
    def __init__(self):
        self.canvas_base_pixel_x = 20
        self.canvas_base_pixel_y = 45

        self.init_graphics()
        self.init_values()

    def init_values(self):
        self.pixel_color_picked    = Color(hexcode='#1f77b4', name='default_pixel')
        self.grouting_color_picked = self.tileParams.GROUTING_COLOR
        
        self.tool_picked = '-Brush-'
    
    def init_graphics(self):
        self.graph = sg.Graph((500, 500), (0, 0), (450, 450),
                              key='-GRAPH-',
                              change_submits=True,
                              drag_submits=False,
                              background_color='lightblue')
        # ------ Menu Definition ------ #
        menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']],
                    ['&Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                    ['&Help', '&About...'], ]

        left_pane = [
          [sg.Menu(menu_def, tearoff=True)],
          [sg.Text('Tile Size', font='ANY 15')],
          [sg.Text('Height: ', size=(12,1)), sg.In(k='-TILE_HEIGHT-', size=(10,1))],
          [sg.Text('Width: ' , size=(12,1)), sg.In(k='-TILE_WIDTH-' , size=(10,1))],

          [sg.Text('Pixel Size', font='ANY 15')],
          [sg.Text('Height: ', size=(12,1)), sg.In(k='-UNIT_HEIGHT-', size=(10,1))],
          [sg.Text('Width: ' , size=(12,1)), sg.In(k='-UNIT_WIDTH-' , size=(10,1))],

          [sg.Text('Grouting Size', font='ANY 15'), 
             sg.Slider(range=(1, 5), default_value=1,
                       orientation='h',
                       key='-GROUTING_SIZE-',
                       enable_events=True,
                       size=(15, 15)),],
          [sg.HorizontalSeparator()],

          [sg.Text('Pixel Color', font='ANY 15', size=(12,1)),
           sg.In("", size=(7, 1), visible=True, enable_events=True, key='-SET_PIXEL_COLOR-', do_not_clear=True),
           sg.ColorChooserButton("", size=(5, 1), target='-SET_PIXEL_COLOR-', button_color=('#1f77b4', '#1f77b4'),
                                 border_width=1, key='-set_pixel_color_chooser-')],
          [sg.Text('Grouting Color', font='ANY 15', size=(12,1)),
           sg.In("", size=(7, 1), visible=True, enable_events=True, key='-SET_GROUTING_COLOR-'),
           sg.ColorChooserButton("", size=(5, 1), target='-SET_GROUTING_COLOR-', button_color=('#1f77b4', '#1f77b4'),
                                 border_width=1, key='-set_grouting_color_chooser-')],
          [sg.HorizontalSeparator()],

          [sg.Frame(layout=[
              [sg.CBox('Vertical Symmetry',   default=True, key='-VERITICAL_SYMM-' ),
              sg.CBox('Horizontal Symmetry', default=True, key='-HORIZONTAL_SYMM-')]
             ],
             title='Symmetry', relief=sg.RELIEF_SUNKEN, tooltip='Check one or multiple')],
          [sg.HorizontalSeparator()],

          [sg.Radio('Brush',        'tool_name', key='-Brush-',        enable_events=True, default=True),
           sg.Radio('Eraser',       'tool_name', key='-Eraser-',       enable_events=True),
           sg.Radio('Paint Bucket', 'tool_name', key='-Paint_Bucket-', enable_events=True),
           sg.Radio('Color Picker', 'tool_name', key='-Color_Picker-', enable_events=True)],
          [sg.HorizontalSeparator()],

          [sg.Ok(button_text='Generate', key='-Generate-'), sg.Cancel()]]
        
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

        self.init_image()

    def init_image(self):
        self.tileParams = TileParams()
        
        self.grid = Grid(self.tileParams, self.canvas_base_pixel_x, self.canvas_base_pixel_y)
        self.grid.generate_grid()
        self.update_canvas(self.grid.image)

    def event_loop(self):
        past_event = None
        while True:
            event, values = self.window.read(timeout=0)

            # TEMP FIX: this bit of logic prevents consecutive repeat event to be processed multiple times
            if (event in ['-SET_GROUTING_COLOR-', '-SET_PIXEL_COLOR-', 'Save']):
              if past_event is not None:
                continue
              else:
                past_event = event
            elif (past_event is not None and event != past_event) or \
                  event in ['-set_grouting_color_chooser-', '-set_pixel_color_chooser-']:
              past_event = None

            if event == 'Cancel' or event == sg.WIN_CLOSED:
                print("CANCEL seen")
                break
            elif event == '-SET_PIXEL_COLOR-':
                print("Pixel Color picked:", values[event])
                pixel_color_picked = Color()
                ret = pixel_color_picked.from_hex(values[event], name='pixel_color_picked')
                if ret is not False and pixel_color_picked != self.pixel_color_picked:
                  self.pixel_color_picked = pixel_color_picked
                  self.window['-set_pixel_color_chooser-'].Update(button_color=(values[event], values[event]))

            elif event == '-SET_GROUTING_COLOR-':
                print("Grouting Color picked:", values[event])
                grouting_color_picked = Color()
                ret = grouting_color_picked.from_hex(values[event], name='grouting_color_picked')
                if ret is not False and grouting_color_picked != self.grouting_color_picked:
                  self.grouting_color_picked = grouting_color_picked
                  self.window['-set_grouting_color_chooser-'].Update(button_color=(values[event], values[event]))
                  
                  image = self.grid.change_grouting_color(self.grouting_color_picked)
                  self.update_canvas(image)
                  # self.generate_new_tile(values)
            elif event in ['-Eraser-', '-Brush-', '-Paint_Bucket-', '-Color_Picker-']:
              print('Radio Button called with ', event)
              self.tool_picked = event
            elif event == '-CANVAS-':
              # print(values[event])
              
              if self.tool_picked == '-Eraser-':
                pixel_color_picked = Color(r=255,g=255,b=255,name='white')
              elif self.tool_picked == '-Brush-':
                pixel_color_picked = self.pixel_color_picked
              else:
                continue
              
              pixel_color, gr_color = self.grid.get_pixel_color(pixel_x=values[event][0], pixel_y=values[event][1])
              if pixel_color is None or gr_color is None:
                continue
              if pixel_color.compare(pixel_color_picked) is True and \
                  gr_color.compare(self.grouting_color_picked) is True: 
                # print("pixel_color, gr_color is same. no need to do anything")
                continue 
              else:
                image = self.grid.color_pixel(self.grid.image, values[event][0], values[event][1], pixel_color_picked)
                self.update_canvas(image)

            elif event == 'Save':
              self.grid.save()
              print('Image saved')

            elif event == '-Generate-':
              print("Generate pressed! tile_height: ", values['-TILE_HEIGHT-'],  "tile_width: ", values['-TILE_WIDTH-'])
              self.generate_new_tile(values)
    
    def generate_new_tile(self, values):
        height      = values['-TILE_HEIGHT-']
        width       = values['-TILE_WIDTH-']
        unit_height = values['-UNIT_HEIGHT-']
        unit_width  = values['-UNIT_WIDTH-']
        grouting_size = values['-GROUTING_SIZE-']

        vertical_symm = values['-VERITICAL_SYMM-']
        horizontal_symm = values['-HORIZONTAL_SYMM-']

        try:
          height=int(height)
        except ValueError:
          height=None

        try:
          width=int(width)
        except ValueError:
          width=None

        try:
          unit_height=int(unit_height)
        except ValueError:
          unit_height=None
          
        try:
          unit_width=int(unit_width)
        except ValueError:
          unit_width=None

        try:
          grouting_size=int(grouting_size)
        except ValueError:
          grouting_size=None
        
        graph = self.window["-CANVAS-"]
        graph.erase()

        self.tileParams.update_params(TILE_WIDTH=width, TILE_HEIGHT=height,
                      rectangle_width=unit_width, rectangle_height=unit_height,
                      GROUTING_SIZE=grouting_size,
                      vertical_symm=vertical_symm, horizontal_symm=horizontal_symm)
        self.tileParams.update_color(GROUTING_COLOR=self.grouting_color_picked)
        self.grid = Grid(self.tileParams, self.canvas_base_pixel_x, self.canvas_base_pixel_y)
        self.grid.generate_grid()
        self.update_canvas(self.grid.image)
    
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
