import numpy
import PySimpleGUI as sg
from base_classes import array_to_data, Color, convert_to_int
from generator import Grid
from input_params import TileParams

# sg.theme('Dark Teal')

class App:
    def __init__(self):
        self.canvas_dimensions = [800, 1000]
        self.canvas_base_pixel_x = 20
        self.canvas_base_pixel_y = 45 

        self.tiled_view_dimensions = [400,400]
        self.tiled_base_pixel_x = 0
        self.tiled_base_pixel_y = 0

        self.blend_mode_color_count = 5
        self.blend_mode_on = True
        self.blend_mode_selections = {str(i):{f'-BLEND_COLOR{i}-'        :None, 
                                              f'-BLEND_COLOR{i}_PERCENT-':0} 
                    for i in range(self.blend_mode_color_count)}
        self.bg_color_picked = Color(hexcode='#808080', name='bg_default')

        self.disabled_color = Color(hexcode='#808080', name='bg_default')
        self.enabled_color  = Color(hexcode='#ffffff', name='bg_default')

        self.init_values()
        self.init_graphics()

    def init_values(self):
        self.tileParams = TileParams()
        self.pixel_color_picked    = Color(hexcode='#1f77b4', name='default_pixel')
        self.grouting_color_picked = self.tileParams.GROUTING_COLOR
        
        self.tool_picked = '-Brush-'
        self.tiled_view_mode = '-TILED_Rotated-'
    
    def init_graphics(self):
        self.graph = sg.Graph((500, 500), (0, 0), (450, 450),
                              key='-GRAPH-',
                              change_submits=True,
                              drag_submits=False,
                              background_color='lightblue')
        # ------ Menu Definition ------ #
        menu_def = [['&File', ['&Open', '&Save', 'Save &Tiled View', 'E&xit', 'Properties']],
                    ['&Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                    ['&Help', '&About...'], ]

        # ------ EITHER THIS  ------ #
        single_bg_color_menu = [
            [sg.Text(f'Background', font='ANY 10', size=(12,1)),
            sg.In("", size=(7, 1), enable_events=True, key=f'-SET_BG_COLOR-', do_not_clear=True),
            sg.ColorChooserButton("", size=(5, 1), target=f'-SET_BG_COLOR-', button_color=('#808080', '#808080'),
                                  border_width=1, key=f'-bg_color_chooser-')]
          ]
        # ------ OR THIS  ------ #
        blend_mode_color_sel = [
            [sg.Text(f'Color#{i}', font='ANY 10', size=(12,1)),
            sg.In("", size=(7, 1), enable_events=True, key=f'-BLEND_COLOR{i}-', do_not_clear=True),
            sg.ColorChooserButton("", size=(5, 1), target=f'-BLEND_COLOR{i}-', button_color=('#1f77b4', '#1f77b4'),
                                  border_width=1, key=f'-blend_color_chooser{i}-'),
            sg.In("0", size=(7, 1), enable_events=True, key=f'-BLEND_COLOR{i}_PERCENT-', do_not_clear=True)]
            for i in range(self.blend_mode_color_count)
          ]

        unit_size = [[sg.Text('Pixel Size', font='ANY 15')],
          [sg.Text('Height: ', size=(10,1)), sg.In(k='-UNIT_HEIGHT-', size=(8,1), enable_events=True)],
          [sg.Text('Width: ' , size=(10,1)), sg.In(k='-UNIT_WIDTH-' , size=(8,1), enable_events=True)]]
        unit_number = [[sg.Text('Pixel Number', font='ANY 15')],
          [sg.Text('Num Height: ', size=(10,1)), sg.In(k='-UNIT_NUM_HEIGHT-', size=(8,1), enable_events=True)],
          [sg.Text('Num Width: ' , size=(10,1)), sg.In(k='-UNIT_NUM_WIDTH-' , size=(8,1), enable_events=True)]]

        left_pane = [
          [sg.Menu(menu_def, tearoff=True)],
          [sg.Text('Tile Size', font='ANY 15')],
          [sg.Text('Height: ', size=(12,1)), sg.In(k='-TILE_HEIGHT-', size=(10,1))],
          [sg.Text('Width: ' , size=(12,1)), sg.In(k='-TILE_WIDTH-' , size=(10,1))],

          [sg.Column(unit_size), sg.Column(unit_number)],

          [sg.Text('Grouting Size', font='ANY 15'), 
             sg.Slider(range=(1, 5), default_value=1,
                       orientation='h',
                       key='-GROUTING_SIZE-',
                       enable_events=True,
                       size=(15, 15)),],
          [sg.HorizontalSeparator()],

          [sg.Checkbox('Blend Mode', enable_events=True, key='-BLEND_MODE-', default=self.blend_mode_on)],
          [self.collapse(blend_mode_color_sel, 'blend_mode_menu'  , self.blend_mode_on)],
          [self.collapse(single_bg_color_menu, 'single_color_menu', not self.blend_mode_on)],
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
              [sg.CBox('Vertical Symmetry',   default=True , key='-VERITICAL_SYMM-' , enable_events=True, size=(15, 1)),
               sg.CBox('Horizontal Symmetry', default=True , key='-HORIZONTAL_SYMM-', enable_events=True, size=(15, 1))],
              [sg.CBox('Left Diagonal',       default=False, key='-LEFT_D_SYMM-',     enable_events=True, size=(15, 1)),
               sg.CBox('Right Diagonal',      default=False, key='-RIGHT_D_SYMM-' ,   enable_events=True, size=(15, 1))]
             ],
             title='Symmetry', relief=sg.RELIEF_SUNKEN, tooltip='Check one or multiple')],
          [sg.HorizontalSeparator()],

          [sg.Radio('Brush',        'tool_name', key='-Brush-',        enable_events=True, default=True),
           sg.Radio('Eraser',       'tool_name', key='-Eraser-',       enable_events=True),
          #  sg.Radio('Paint Bucket', 'tool_name', key='-Paint_Bucket-', enable_events=True),
           sg.Radio('Color Picker', 'tool_name', key='-Color_Picker-', enable_events=True)],
          [sg.HorizontalSeparator()],
          
          [sg.Ok(button_text='Generate', key='-Generate-'), sg.Cancel()]]
        
        work_canvas = sg.Graph(
          canvas_size=(self.canvas_dimensions[0], self.canvas_dimensions[1]),
          graph_bottom_left=(0, self.canvas_dimensions[1]),
          graph_top_right=(self.canvas_dimensions[0], 0),
          key="-CANVAS-",
          change_submits=True,  # mouse click events
          background_color='lightblue',
          drag_submits=True)
        
        tiled_canvas = sg.Graph(
          canvas_size=(self.tiled_view_dimensions[0], self.tiled_view_dimensions[1]),
          graph_bottom_left=(0, self.tiled_view_dimensions[1]),
          graph_top_right=(self.tiled_view_dimensions[0], 0),
          key="-TILED_CANVAS-",
          change_submits=False,  # mouse click events
          background_color='lightblue',
          drag_submits=False)
        
        right_pane = [
          [sg.Button(button_text='Update titled view', key='-UPDATE_TITLED_VIEW-')],
          [sg.Radio('Rotated',  'tile_mode', key='-TILED_Rotated-' , enable_events=True, default=True),
           sg.Radio('Repeated', 'tile_mode', key='-TILED_Repeated-', enable_events=True)],
          [sg.HorizontalSeparator()],
          [tiled_canvas]
        ]
        layout = [
          [sg.Column(left_pane), work_canvas, sg.Column(right_pane)]
        ]
        self.window = sg.Window('Application', layout, finalize=True)

        self.gen_new_image()

    def gen_new_image(self):
        graph = self.window["-CANVAS-"]
        graph.erase()

        self.grid = Grid(self.tileParams, self.canvas_base_pixel_x, self.canvas_base_pixel_y)
        self.grid.generate_grid()
        self.update_canvas(self.grid.image)

    def event_loop(self):
        past_event = None
        while True:
            event, values = self.window.read(timeout=1)

            # TEMP FIX: this bit of logic prevents consecutive repeat event to be processed multiple times
            if (event in ['-SET_PIXEL_COLOR-', 'Save']):
              if past_event is not None:
                continue
              else:
                past_event = event
            elif (past_event is not None and event != past_event) or \
                  event in ['-set_pixel_color_chooser-']:
              past_event = None

            if event == 'Cancel' or event == sg.WIN_CLOSED:
                print("CANCEL seen")
                break
            elif event == '-BLEND_MODE-':
                self.blend_mode_on = not self.blend_mode_on
                self.window['blend_mode_menu'  ].update(visible =     self.blend_mode_on)
                self.window['single_color_menu'].update(visible = not self.blend_mode_on)

            elif event == '-SET_PIXEL_COLOR-':
                ret = self.pick_color(hex_code=values[event],
                                      stored_value=self.pixel_color_picked,
                                      name='pixel_color_picked')
                if ret is not False:
                  self.pixel_color_picked = ret
                  print("Pixel Color picked:", values[event])
                  self.window['-set_pixel_color_chooser-'].Update(button_color=(values[event], values[event]))

            elif event == '-SET_GROUTING_COLOR-':
                ret = self.pick_color(hex_code=values[event],
                                      stored_value=self.grouting_color_picked,
                                      name='grouting_color_picked')
                if ret is not False:
                  self.grouting_color_picked = ret
                  self.window['-set_grouting_color_chooser-'].Update(button_color=(values[event], values[event]))

                  self.grid.change_grouting_color(self.grouting_color_picked)
                  self.update_canvas(self.grid.image)

            elif event.startswith('-UNIT_'):
                self.window[event].Update(background_color=self.enabled_color.get_hex())
                mode = "pixel_number" if "NUM" in event else "pixel_size"
                self.update_unit_options_en_disable(mode)

            elif event == '-SET_BG_COLOR-':
                ret = self.pick_color(hex_code=values[event],
                                      stored_value=self.bg_color_picked, 
                                      name='bg_color_picked')
                if ret is not False:
                  self.bg_color_picked = ret
                  self.window[f'-bg_color_chooser-'].Update(button_color=(values[event], values[event]))
            elif event.startswith('-BLEND_COLOR'):
              event_str = event
              color_num = event_str.strip("-BLEND_COLOR_PERCENT-")
              if event.endswith('PERCENT-'):
                try:
                  value = int(values[event])
                  if value>100:
                    raise ValueError
                  self.blend_mode_selections[color_num][event] = value
                  print(f"Updating percent of blend_color{color_num} to {value}")
                except ValueError:
                  continue
              else:
                # print(f"color event seen :{color_num}")
                ret = self.pick_color(hex_code=values[event], 
                            stored_value=self.blend_mode_selections[color_num][event],
                            name=f'blend_color{color_num}_picked')
                if ret is not False:
                  self.blend_mode_selections[color_num][event] = ret
                  # print(f"Updating blend_color{color_num} to {ret}")
                  self.window[f'-blend_color_chooser{color_num}-'].Update(button_color=(values[event], values[event]))

            elif event.endswith('_SYMM-'):
              print(f"{event} called")
              self.update_tileparams(values)
              self.grid.update_symm(self.tileParams)

            elif event in ['-Eraser-', '-Brush-', '-Paint_Bucket-', '-Color_Picker-']:
              print('Radio Button called with ', event)
              self.tool_picked = event
            elif event.startswith('-TILED_'):
              print('Tiled view changed to ', event)
              self.tiled_view_mode = event
            elif event == '-CANVAS-':
              # print(values[event])
              
              pixel_color, gr_color = self.grid.get_pixel_color(pixel_x=values[event][0], pixel_y=values[event][1])

              if self.tool_picked == '-Eraser-':
                pixel_color_picked = self.bg_color_picked
              elif self.tool_picked == '-Brush-':
                pixel_color_picked = self.pixel_color_picked
              elif self.tool_picked == '-Color_Picker-':
                self.window['-SET_PIXEL_COLOR-'].Update(pixel_color.get_hex())
                self.window['-set_pixel_color_chooser-'].Update(button_color=
                                (pixel_color.get_hex(), pixel_color.get_hex()))
                self.pixel_color_picked = pixel_color
                continue
              elif self.tool_picked == '-Paint_Bucket-':
                continue
              
              if pixel_color is None or gr_color is None:
                # print("OUT OF BOUNDS")
                continue
              if pixel_color.compare(pixel_color_picked) is True and \
                  gr_color.compare(self.grouting_color_picked) is True: 
                # print("pixel_color, gr_color is same. no need to do anything")
                continue 
              else:
                self.grid.color_pixel(self.grid.image, values[event][0], values[event][1], pixel_color_picked)
                self.update_canvas(self.grid.image)

            elif event.startswith('Save'):
              file_loc = sg.popup_get_file('Save as', no_window=True, modal=True,
                        default_extension = 'png',
                        save_as=True, file_types=(('PNG', '.png'), ('JPG', '.jpg')))
              if file_loc == '':
                continue
              if event == "Save Tiled View":
                print('Saving tiled view to:', file_loc)
                self.grid.save(filename=file_loc)
              else:
                print('Saving to:', file_loc)
                self.grid.save(filename=file_loc)

            elif event == '-UPDATE_TITLED_VIEW-':
              self.update_titled_view(self.grid.image)
            elif event == '-Generate-':
              print("Generate pressed! tile_height: ", values['-TILE_HEIGHT-'],  "tile_width: ", values['-TILE_WIDTH-'])
              self.update_tileparams(values)
              self.gen_new_image()
    
    def update_tileparams(self, values):
        height        = convert_to_int(values['-TILE_HEIGHT-'])
        width         = convert_to_int(values['-TILE_WIDTH-'])

        unit_height     = convert_to_int(values['-UNIT_HEIGHT-'])
        unit_width      = convert_to_int(values['-UNIT_WIDTH-'])
        unit_num_height = convert_to_int(values['-UNIT_NUM_HEIGHT-'])
        unit_num_width  = convert_to_int(values['-UNIT_NUM_WIDTH-'])

        grouting_size = convert_to_int(values['-GROUTING_SIZE-'])

        vertical_symm   = values['-VERITICAL_SYMM-']
        horizontal_symm = values['-HORIZONTAL_SYMM-']
        right_d_symm    = values['-RIGHT_D_SYMM-']
        left_d_symm     = values['-LEFT_D_SYMM-']


        self.tileParams.update_params(TILE_WIDTH=width, TILE_HEIGHT=height,
                      GROUTING_SIZE=grouting_size,
                      rectangle_width=unit_width, rectangle_height=unit_height,
                      num_width=unit_num_width, num_height=unit_num_height,
                      vertical_symm=vertical_symm, horizontal_symm=horizontal_symm,
                      right_d_symm=right_d_symm, left_d_symm=left_d_symm)

        #update the grouting and the blend/bg colors
        self.tileParams.update_color(GROUTING_COLOR=self.grouting_color_picked)
        if self.blend_mode_on is True:
          self.tileParams.update_color(BLEND_MODE_COLORS=self.blend_mode_selections)
        else:
          self.tileParams.update_color(SOLID_BG_COLOR=self.bg_color_picked)

        self.update_unit_options_en_disable(self.tileParams.mode)
        self.window['-TILE_WIDTH-' ].Update(self.tileParams.NEW_TILE_PX_WIDTH //self.tileParams.PIXELS_PER_MM)
        self.window['-TILE_HEIGHT-'].Update(self.tileParams.NEW_TILE_PX_HEIGHT//self.tileParams.PIXELS_PER_MM)

    def update_unit_options_en_disable(self, mode):
        if mode == "pixel_size":
          self.window[f'-UNIT_HEIGHT-'    ].Update(background_color=self.enabled_color.get_hex())
          self.window[f'-UNIT_WIDTH-'     ].Update(background_color=self.enabled_color.get_hex())
          self.window[f'-UNIT_NUM_HEIGHT-'].Update(background_color=self.disabled_color.get_hex())
          self.window[f'-UNIT_NUM_WIDTH-' ].Update(background_color=self.disabled_color.get_hex())
          self.window[f'-UNIT_NUM_HEIGHT-'].Update("")
          self.window[f'-UNIT_NUM_WIDTH-' ].Update("")
        else:
          self.window[f'-UNIT_HEIGHT-'    ].Update(background_color=self.disabled_color.get_hex())
          self.window[f'-UNIT_WIDTH-'     ].Update(background_color=self.disabled_color.get_hex())
          self.window[f'-UNIT_NUM_HEIGHT-'].Update(background_color=self.enabled_color.get_hex())
          self.window[f'-UNIT_NUM_WIDTH-' ].Update(background_color=self.enabled_color.get_hex())
          self.window[f'-UNIT_HEIGHT-'    ].Update("")
          self.window[f'-UNIT_WIDTH-'     ].Update("")

    def update_canvas(self, image):
        graph = self.window["-CANVAS-"]
        data = array_to_data(image)
        graph.draw_image(data=data, location=(self.canvas_base_pixel_x, self.canvas_base_pixel_y))

    def update_titled_view(self, image):
        graph = self.window["-TILED_CANVAS-"]
        self.grid.update_tiled_image(image, mode=self.tiled_view_mode)
        data = array_to_data(self.grid.tiled_image, 
                      resize=self.tiled_view_dimensions)
        graph.draw_image(data=data, location=(self.tiled_base_pixel_x, self.tiled_base_pixel_y))

    def play(self):
        self.event_loop()

    def pick_color(self, hex_code, stored_value, name=None):
      color_picked = Color()
      ret = color_picked.from_hex(hex_code, name='color_picked')
      if ret is not False and not color_picked.compare(stored_value):
        print("Color picked:" if name is None else name, hex_code, color_picked, stored_value)
        return color_picked
      else:
        return False

    def collapse(self, layout, key, visible):
      return sg.pin(sg.Column(layout, key=key, visible=visible))

if (__name__ == "__main__"):
    game = App()
    game.play()
    sg.popup('Completed running.', 'Click OK to exit the program')
    game.window.close()
