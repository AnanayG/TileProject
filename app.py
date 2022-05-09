import numpy
import PySimpleGUI as sg

sg.theme('Dark Teal')

class App:
    def __init__(self):
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
        column2 = [
          [sg.Text('Tile Size', font='ANY 15')],
          [sg.Text('Length: ', size=(12,1)), sg.In(k='-TILE_LEN-', size=(10,1))],
          [sg.Text('Width: ', size=(12,1)), sg.In(k='-TILE_WIDTH-', size=(10,1))],
        ]
        # ------ Menu Definition ------ #
        menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']],
                    ['&Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                    ['&Help', '&About...'], ]

        layout = [
          [sg.Menu(menu_def, tearoff=True)],
          [sg.Text('Tile Size', font='ANY 15')],
          [sg.Text('Length: ', size=(12,1)), sg.In(k='-TILE_LEN-', size=(10,1))],
          [sg.Text('Width: ', size=(12,1)), sg.In(k='-TILE_WIDTH-', size=(10,1))],
          [sg.Text('Pixel Size', font='ANY 15')],
          [sg.Text('Length: ', size=(12,1)), sg.In(k='-PIXEL_LEN-', size=(10,1))],
          [sg.Text('Width: ', size=(12,1)), sg.In(k='-PIXEL_WIDTH-', size=(10,1))],
          [sg.Column(column1, element_justification='c'), sg.Column(column2, element_justification='c')],
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

        self.window = sg.Window('Application', layout, finalize=True)
        event, values = self.window.read(timeout=0)
    
    def draw_board(self):
        while True:
            event, values = self.window.read()
            if event == 'Cancel' or event == sg.WIN_CLOSED:
                break
            elif event == 'set_color':
                self.window['set_color_chooser'].Update(button_color=(values[event], values[event]))

    def play(self):
        self.draw_board()


if (__name__ == "__main__"):
    game = App()
    game.play()
    sg.popup('Completed running.', 'Click OK to exit the program')
    game.window.close()
