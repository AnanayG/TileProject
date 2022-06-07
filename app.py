from math import ceil
import PySimpleGUI as sg
from base_classes import Color, Failure, convert_to_int
from generator import Grid
from display_image import colorSelectorTkWindow, about_me
from input_params import TileParams
import pickle
from PIL import Image, ImageTk, ImageGrab

# sg.theme('Dark Teal')

class App:
    def __init__(self):
        self.canvas_dimensions = [800, 1000]
        self.canvas_base_pixel_x = 20
        self.canvas_base_pixel_y = 45
        self.canvas_visible_area = (0, 0,
                 self.canvas_dimensions[0], self.canvas_dimensions[1])

        self.tiled_view_px_dimensions = [400,400]
        self.room_dimensions          = [1200, 1200]
        self.tiled_base_pixel_x = 0
        self.tiled_base_pixel_y = 0

        self.imscale = 1.0           # scale for the canvas image
        self.tiled_view_scale = 1.0  # inverse scale for the tiled image
        self.delta   = 1.3  # zoom step magnitude

        self.keyboard_mapping_to_event = {'r':'-Brush-' , 'R':'-Brush-',
                                          'e':'-Eraser-', 'E':'-Eraser-',
                                          'g':'-Color_Swapper-', 'G':'-Color_Swapper-',
                                          'h':'-Color_Picker-', 'H':'-Color_Picker-',
                                 ' ':'-UPDATE_TITLED_VIEW-'}
        self.tool_to_canvas_cursor = {'-Brush-'         :'plus',
                                      '-Eraser-'        :'dot',
                                      '-Color_Swapper-' :'crosshair',
                                      '-Color_Picker-'  :'crosshair'}
        
        self.blend_mode_color_count = 5
        self.blend_mode_on = True
        self.blend_mode_selections = {str(i):{f'-BLEND_COLOR{i}-'        :None, 
                                              f'-BLEND_COLOR{i}_PERCENT-':0} 
                    for i in range(self.blend_mode_color_count)}

        self.bg_color_picked = Color(hexcode='#808080', name='bg_default')
        self.disabled_color  = Color(hexcode='#808080', name='disabled')
        self.enabled_color   = Color(hexcode='#ffffff', name='enabled')

        self.init_values()
        self.init_graphics()

    def init_values(self):
        self.tileParams = TileParams()
        self.pixel_color_picked     = Color(hexcode='#1f77b4', name='default_pixel')
        self.pixel_color_picked_new = Color(hexcode='#1f77b4', name='default_pixel_new')
        self.grouting_color_picked   = self.tileParams.GROUTING_COLOR
        
        self.tool_picked = '-Brush-'
        self.tiled_view_mode = '-TILED_Rotated_CLK-'

        self.add_gloss = False
        self.auto_update_titled_view = False
        self.view_rotated_view_options = True
    
    def init_graphics(self):
        # ------ Menu Definition ------ #
        menu_def = [['&File', ['&Load PTG', 'Save &PTG', '&Save Image', 'Save &Tiled Image','E&xit']],
                    ['&Edit', ['Change &Canvas Color', 'Paste', ['Special', 'Normal', ], 'Undo'], ],
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

        
        pixel_color_swap_menu = [
            [sg.Text(f'New Color', font='ANY 15', size=(12,1)),
            sg.In("", size=(7, 1), enable_events=True, key=f'-SET_PIXEL_COLOR_NEW-', do_not_clear=True),
            sg.ColorChooserButton("", size=(5, 1), target=f'-SET_PIXEL_COLOR_NEW-', button_color=('#1f77b4', '#1f77b4'),
                                  border_width=1, key=f'-set_new_pixel_color_chooser-'),
            sg.Button(button_text='Change', key='-PIXEL_COLOR_SWAP_BUTTON-')]
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
          [self.collapse(pixel_color_swap_menu, 'pixel_color_swap_menu', self.tool_picked=='-Color_Swapper-')],
          [sg.HorizontalSeparator()],
          
          [sg.Text('Grouting Color', font='ANY 15', size=(12,1)),
           sg.In("", size=(7, 1), visible=True, enable_events=True, key='-SET_GROUTING_COLOR-'),
           sg.ColorChooserButton("", size=(5, 1), target='-SET_GROUTING_COLOR-', button_color=('#1f77b4', '#1f77b4'),
                                 border_width=1, key='-set_grouting_color_chooser-')],
          [sg.HorizontalSeparator()],

          [sg.Checkbox('Gloss', enable_events=True, key='-GLOSS-', default=self.add_gloss)],
          [sg.HorizontalSeparator()],

          [sg.Frame(layout=[
              [sg.CBox('Vertical Symmetry',   default=True , key='-VERITICAL_SYMM-' , enable_events=True, size=(15, 1)),
               sg.CBox('Horizontal Symmetry', default=True , key='-HORIZONTAL_SYMM-', enable_events=True, size=(15, 1))],
              [sg.CBox('Left Diagonal',       default=False, key='-LEFT_D_SYMM-',     enable_events=True, size=(15, 1)),
               sg.CBox('Right Diagonal',      default=False, key='-RIGHT_D_SYMM-' ,   enable_events=True, size=(15, 1))]
             ],
             title='Symmetry', relief=sg.RELIEF_SUNKEN, tooltip='Check one or multiple')],
          [sg.HorizontalSeparator()],

          [sg.Radio('Brush',        'tool_name', key='-Brush-',         enable_events=True, tooltip='Press r ', default=True),
           sg.Radio('Eraser',       'tool_name', key='-Eraser-',        enable_events=True, tooltip='Press e '),
           sg.Radio('Color Swap'  , 'tool_name', key='-Color_Swapper-', enable_events=True, tooltip='Press g '),
           sg.Radio('Color Picker', 'tool_name', key='-Color_Picker-',  enable_events=True, tooltip='Press h ')],
          [sg.HorizontalSeparator()],
          
          [sg.Ok(button_text='Generate', key='-Generate-'), sg.Cancel()]
        ]
        
        work_canvas = sg.Graph(
          canvas_size=(self.canvas_dimensions[0], self.canvas_dimensions[1]),
          graph_bottom_left=(0, self.canvas_dimensions[1]),
          graph_top_right=(self.canvas_dimensions[0], 0),
          key="-CANVAS-",
          change_submits=True,  # mouse click events
          background_color='lightblue',
          drag_submits=True)
        
        tiled_canvas = sg.Graph(
          canvas_size=(self.tiled_view_px_dimensions[0], self.tiled_view_px_dimensions[1]),
          graph_bottom_left=(0, self.tiled_view_px_dimensions[1]),
          graph_top_right=(self.tiled_view_px_dimensions[0], 0),
          key="-TILED_CANVAS-",
          change_submits=False,  # mouse click events
          background_color='lightblue',
          drag_submits=False)
        
        rotated_view_options = [
          [sg.Radio('Clockwise', 'rotated_mode_options', key='-TILED_Rotated_CLK-' , enable_events=True, default=True),
           sg.Radio('Anticlockwise', 'rotated_mode_options', key='-TILED_Rotated_ANTI_CLK-' , enable_events=True)]
        ]
        right_pane = [
          [sg.Text('Room Size', font='ANY 15')],
          [sg.Column([[sg.Text('Height: ', size=(12,1)), sg.In(k='-ROOM_HEIGHT-', size=(10,1), default_text=self.room_dimensions[0])]]),
           sg.Column([[sg.Text('Width: ' , size=(12,1)), sg.In(k='-ROOM_WIDTH-' , size=(10,1), default_text=self.room_dimensions[1])]])],
          [sg.HorizontalSeparator()],

          [sg.Checkbox('Auto Update Tiled View', enable_events=True, key='-AUTO_UPDATE_TITLED_VIEW-', default=self.auto_update_titled_view)],
          [sg.Button(button_text='Update titled view', key='-UPDATE_TITLED_VIEW-', tooltip='Press SPACE')],
          [sg.Radio('Rotated',  'tile_mode', key='-TILED_Rotated-' , enable_events=True, default=True),
           sg.Radio('Mirrored', 'tile_mode', key='-TILED_Mirrored-' , enable_events=True),
           sg.Radio('Repeated', 'tile_mode', key='-TILED_Repeated-', enable_events=True)],
          [self.collapse(rotated_view_options, '-TILED_Rotated_options-', self.view_rotated_view_options)],
          [sg.HorizontalSeparator()],

          [tiled_canvas]
        ]
        layout = [
          [sg.Column(left_pane), work_canvas, sg.Column(right_pane)]
        ]
        
        self.window = sg.Window('Application', layout, finalize=True, resizable=True, return_keyboard_events=True)
        self.set_canvas_bindings()
        self.load_image_to_canvas()

    def set_canvas_bindings(self):
        #these are used for canvas, shouldn't change anything for the whole application
        self.window.TKroot.unbind('<Control-ButtonPress-1>')
        self.window.TKroot.unbind('<Control-B1-Motion>')
        
        self.canvas       = self.window['-CANVAS-'].Widget
        self.tiled_canvas = self.window['-TILED_CANVAS-'].Widget

        self.canvas.config(cursor=self.tool_to_canvas_cursor['-Brush-'])
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<Control-ButtonPress-1>', self.move_from)
        self.canvas.bind('<Control-B1-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        '''
        Uncomment the following 3 lines, then zoom will only work
        inside the TILE area
        '''
        # bbox = self.canvas.bbox(self.container)  # get image area
        # if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        # else: return  # zoom only inside image area

        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        print(f"CHANGING SCALE {x=} {y=} {scale=} {self.imscale=}")
        self.show_image()

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)
        self.move_from_pos = (event.x, event.y)
    
    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image
    
    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        # 1. this is the bounding box of the image
        bbox1 = self.canvas.bbox(self.container)
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        self.canvas_image_bb = bbox1

        # 2. get visible area of the canvas
        bbox2 = (self.canvas.canvasx(0), 
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        self.canvas_visible_area = bbox2
        

        # 3. this configures the scrollregion, if a scroll bar is needed.
        # bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
        #         max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        # if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
        #     bbox[0] = bbox1[0]
        #     bbox[2] = bbox1[2]
        # if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
        #     bbox[1] = bbox1[1]
        #     bbox[3] = bbox1[3]
        # self.canvas.configure(scrollregion=bbox)  # set scroll region

        # 4. (x1,y1,x2,y2) is the coordinates of the image tile inside the VISIBLE canvas
        x1 = max(bbox2[0] - bbox1[0], 0)  
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

    def load_image_to_canvas(self, grid_image_arr=None):
        graph = self.window["-CANVAS-"]
        graph.erase()

        self.grid = Grid(self.tileParams)
        if grid_image_arr is not None:
          self.grid.load_from_array(grid_image_arr)
        else:
          self.grid.generate_grid(self.blend_mode_on)

        (self.height, self.width, depth) = self.grid.image.shape

        base_x, base_y = (self.canvas_base_pixel_x + self.canvas_visible_area[0],
                          self.canvas_base_pixel_y + self.canvas_visible_area[1])
        self.container = self.canvas.create_rectangle(base_x, base_y,
                    base_x+self.width, base_y+self.height, width=0)
        
        self.update_canvas_from_arr(self.grid.image)

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

            #if the event if a KEYBOARD INPUT then change the event variable
            if event in self.keyboard_mapping_to_event.keys():
              event = self.keyboard_mapping_to_event[event]
              if event != "-UPDATE_TITLED_VIEW-":
                self.window[event].Update(value=True)

            if event in ['Cancel', 'Exit'] or event == sg.WIN_CLOSED:
                print("CANCEL seen")
                break
            if event == 'About...':
                about_me()
            elif event == '-BLEND_MODE-':
                self.blend_mode_on = not self.blend_mode_on
                self.window['blend_mode_menu'  ].update(visible =     self.blend_mode_on)
                self.window['single_color_menu'].update(visible = not self.blend_mode_on)
            elif event == '-GLOSS-':
                self.add_gloss = not self.add_gloss
                self.grid.add_gloss_effect(self.add_gloss)
                self.update_canvas_from_arr(self.grid.image)

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
                  self.update_canvas_from_arr(self.grid.image)
            elif event == '-GROUTING_SIZE-':
                self.window.Element('-CANVAS-').SetFocus()
                self.grid.change_grouting_size(int(values[event]))
                self.update_canvas_from_arr(self.grid.image)
            
            elif event.startswith('-UNIT_'):
                self.window[event].Update(background_color=self.enabled_color.get_hex())
                mode = "pixel_number" if "NUM" in event else "pixel_size"
                self.update_unit_options_en_disable(mode)

            elif event == '-SET_PIXEL_COLOR_NEW-':
                ret = self.pick_color(hex_code=values[event],
                                      stored_value=self.pixel_color_picked_new, 
                                      name='bg_color_picked')
                if ret is not False:
                  self.pixel_color_picked_new = ret
                  self.window[f'-set_new_pixel_color_chooser-'].Update(button_color=(values[event], values[event]))
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

            elif event == '-PIXEL_COLOR_SWAP_BUTTON-':
              print("SWAPPING colors!")
              self.grid.swapColors(self.pixel_color_picked, self.pixel_color_picked_new)
              self.update_canvas_from_arr(self.grid.image)
              
            elif event.endswith('_SYMM-'):
              print(f"{event} called")
              ret = self.update_tileparams(values)
              if type(ret) is not Failure:
                self.grid.update_symm(self.tileParams)

            elif event in ['-Eraser-', '-Brush-', '-Color_Swapper-', '-Color_Picker-']:
              self.window.Element('-CANVAS-').SetFocus()
              self.window['-CANVAS-'].Widget.config(cursor=self.tool_to_canvas_cursor[event])
              print('Radio Button called with ', event)
              self.tool_picked = event
              self.window['pixel_color_swap_menu'].Update(visible=(event=='-Color_Swapper-'))
            elif event.startswith('-TILED_'):
              print('Tiled view changed to ', event)
              if 'Rotated' in event:
                self.view_rotated_view_options = True
                if values['-TILED_Rotated_CLK-'] is True:
                  self.tiled_view_mode = '-TILED_Rotated_CLK-'
                else:
                  self.tiled_view_mode = '-TILED_Rotated_ANTI_CLK-'
              else:
                self.view_rotated_view_options = False
                self.tiled_view_mode = event
              self.window['-TILED_Rotated_options-'].update(visible=self.view_rotated_view_options)
            
            elif event == '-CANVAS-':
              self.window.Element('-CANVAS-').SetFocus()
              # print(values[event])
              
              x,y = self.convert_pixel_coordinates_to_unit_coordinates(values[event])
              pixel_color, gr_color = self.grid.get_pixel_color(x,y)
              if pixel_color is None or gr_color is None:
                # print("OUT OF BOUNDS")
                continue

              if self.tool_picked == '-Eraser-':
                pixel_color_picked = self.bg_color_picked
              elif self.tool_picked == '-Brush-':
                pixel_color_picked = self.pixel_color_picked
              elif self.tool_picked in ['-Color_Picker-','-Color_Swapper-']:
                self.window['-SET_PIXEL_COLOR-'].Update(pixel_color.get_hex())
                self.window['-set_pixel_color_chooser-'].Update(button_color=
                                (pixel_color.get_hex(), pixel_color.get_hex()))
                self.pixel_color_picked = pixel_color
                continue
              
              if pixel_color.compare(pixel_color_picked) is True and \
                  gr_color.compare(self.grouting_color_picked) is True: 
                # print("pixel_color, gr_color is same. no need to do anything")
                continue 
              else:
                self.grid.color_pixel(self.grid.image, x,y, pixel_color_picked)
                self.update_canvas_from_arr(self.grid.image)
                if self.auto_update_titled_view is True:
                  self.room_dimensions[0] = values['-ROOM_HEIGHT-'] if values['-ROOM_HEIGHT-'] is not None else self.room_dimensions[0]
                  self.room_dimensions[1] = values['-ROOM_WIDTH-' ] if values['-ROOM_WIDTH-'] is not None else self.room_dimensions[1]
                  self.update_titled_view(self.grid.image)

            elif event.startswith('Save'):
              if 'Image' in event:  # Save Image, Save Tiled Image
                file_loc = sg.popup_get_file(event, no_window=True, modal=True,
                          default_extension = 'png',
                          save_as=True, file_types=(('PNG', '.png'), ('JPG', '.jpg')))
              else:                 # Save PTG
                file_loc = sg.popup_get_file(event, no_window=True, modal=True,
                          default_extension = 'ptg',
                          save_as=True, file_types=[('PTG', '.ptg')])

              if file_loc == '':
                continue
              if event == "Save Tiled Image":
                print('Saving tiled view to:', file_loc)
                self.save_tiled_view(file_loc)
              elif event == "Save PTG":
                print('Saving PTG to:', file_loc)
                self.save_ptg(file_loc)
              else:
                print('Saving to:', file_loc)
                self.grid.save_image(filename=file_loc)
            elif event=='Load PTG':
                file_loc = sg.popup_get_file(event, no_window=True, modal=True,
                          default_extension = 'ptg',
                          save_as=False, file_types=[('PTG', '.ptg')])
                if file_loc == '':
                  continue
                print('Loading PTG from:', file_loc)
                self.load_ptg(file_loc)

            elif event == 'Change Canvas Color':
              color = colorSelectorTkWindow()
              print("Canvas Bg Color selected:{}".format(color))
              self.window['-CANVAS-'].Update(background_color=color)

            elif event == '-UPDATE_TITLED_VIEW-':
              self.room_dimensions[0] = values['-ROOM_HEIGHT-'] if values['-ROOM_HEIGHT-'] is not None else self.room_dimensions[0]
              self.room_dimensions[1] = values['-ROOM_WIDTH-' ] if values['-ROOM_WIDTH-'] is not None else self.room_dimensions[1]
              self.update_titled_view(self.grid.image)
            elif event == '-AUTO_UPDATE_TITLED_VIEW-':
              self.auto_update_titled_view = not self.auto_update_titled_view
              self.room_dimensions[0] = values['-ROOM_HEIGHT-'] if values['-ROOM_HEIGHT-'] is not None else self.room_dimensions[0]
              self.room_dimensions[1] = values['-ROOM_WIDTH-' ] if values['-ROOM_WIDTH-'] is not None else self.room_dimensions[1]
              self.update_titled_view(self.grid.image)
            elif event == '-Generate-':
              self.window.Element('-CANVAS-').SetFocus()
              print("Generate pressed! tile_height: ", values['-TILE_HEIGHT-'],  "tile_width: ", values['-TILE_WIDTH-'])
              ret = self.update_tileparams(values)
              if type(ret) is not Failure:
                self.load_image_to_canvas()

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

        ret = self.tileParams.update_params(TILE_WIDTH=width, TILE_HEIGHT=height,
                      GROUTING_SIZE=grouting_size,
                      rectangle_width=unit_width, rectangle_height=unit_height,
                      num_width=unit_num_width, num_height=unit_num_height,
                      vertical_symm=vertical_symm, horizontal_symm=horizontal_symm,
                      right_d_symm=right_d_symm, left_d_symm=left_d_symm)
        if type(ret) is Failure:
          return ret.run()
          
        #update the grouting and the blend/bg colors
        self.tileParams.update_color(GROUTING_COLOR=self.grouting_color_picked)
        if self.blend_mode_on is True:
          ret = self.tileParams.update_color(BLEND_MODE_COLORS=self.blend_mode_selections)
          if type(ret) is Failure:
            return ret.run()
        else:
          self.tileParams.update_color(SOLID_BG_COLOR=self.bg_color_picked)

        self.update_window_from_tileparams()

    def update_unit_options_en_disable(self, mode, new_load=False):
        if mode == "pixel_size":
          self.window[f'-UNIT_HEIGHT-'    ].Update(background_color=self.enabled_color.get_hex())
          self.window[f'-UNIT_WIDTH-'     ].Update(background_color=self.enabled_color.get_hex())
          self.window[f'-UNIT_NUM_HEIGHT-'].Update(background_color=self.disabled_color.get_hex())
          self.window[f'-UNIT_NUM_WIDTH-' ].Update(background_color=self.disabled_color.get_hex())
          self.window[f'-UNIT_NUM_HEIGHT-'].Update("")
          self.window[f'-UNIT_NUM_WIDTH-' ].Update("")
          if new_load is True:
            self.window['-UNIT_WIDTH-' ].Update(self.tileParams.rectangle_width)
            self.window['-UNIT_HEIGHT-'].Update(self.tileParams.rectangle_height)
        else:
          self.window[f'-UNIT_HEIGHT-'    ].Update(background_color=self.disabled_color.get_hex())
          self.window[f'-UNIT_WIDTH-'     ].Update(background_color=self.disabled_color.get_hex())
          self.window[f'-UNIT_NUM_HEIGHT-'].Update(background_color=self.enabled_color.get_hex())
          self.window[f'-UNIT_NUM_WIDTH-' ].Update(background_color=self.enabled_color.get_hex())
          self.window[f'-UNIT_HEIGHT-'    ].Update("")
          self.window[f'-UNIT_WIDTH-'     ].Update("")
          if new_load is True:
            self.window['-UNIT_NUM_WIDTH-' ].Update(self.tileParams.no_per_width)
            self.window['-UNIT_NUM_HEIGHT-'].Update(self.tileParams.no_per_height)
          
        if new_load:
          self.window['-GLOSS-'].Update(self.tileParams.add_gloss)
          self.add_gloss = self.tileParams.add_gloss
          
          self.window['-VERITICAL_SYMM-'].Update(self.tileParams.symmetry['vertical'])
          self.window['-HORIZONTAL_SYMM-'].Update(self.tileParams.symmetry['horizontal'])
          self.window['-RIGHT_D_SYMM-'].Update(self.tileParams.symmetry['right_diagonal'])
          self.window['-LEFT_D_SYMM-'].Update(self.tileParams.symmetry['left_diagonal'])

          gr = self.tileParams.GROUTING_COLOR
          self.window['-set_grouting_color_chooser-'].Update(button_color=(gr.get_hex(), gr.get_hex()))
            
    def convert_pixel_coordinates_to_unit_coordinates(self, selected_pixel):
        true_coordinates = (selected_pixel[0] + self.canvas_visible_area[0],
                            selected_pixel[1] + self.canvas_visible_area[1])

        canvas_image_bb = self.canvas_image_bb
        pixel_x = true_coordinates[0] - canvas_image_bb[0]
        pixel_y = true_coordinates[1] - canvas_image_bb[1]
        
        canvas_width  = canvas_image_bb[2] - canvas_image_bb[0]
        canvas_height = canvas_image_bb[3] - canvas_image_bb[1]

        w_fac = canvas_width/self.tileParams.NEW_TILE_PX_WIDTH
        h_fac = canvas_height/self.tileParams.NEW_TILE_PX_HEIGHT
        
        unit_width  = self.tileParams.pixel_width_plus_grout * w_fac
        unit_height = self.tileParams.pixel_height_plus_grout * h_fac

        # print(f"{canvas_image_bb=} {true_coordinates=} {selected_pixel=} {w_fac=} {h_fac=}")
        # print(f"{pixel_x=} {pixel_y=} {unit_width=} {unit_height=}")

        if (pixel_x >= canvas_width or pixel_x < 0):
            return (None, None)
        if (pixel_y >= canvas_height or pixel_y < 0):
            return (None, None)
        
        x = int(pixel_x/unit_width)
        y = int(pixel_y/unit_height)
        # print(f"{x=} {y=}")

        return (x,y)
        
    def update_canvas_from_arr(self, image):
        self.image = Image.fromarray(image)
        self.show_image()

    def update_titled_view(self, image):
        self.grid.update_tiled_image(image, mode=self.tiled_view_mode)
        tiled_image = Image.fromarray(self.grid.tiled_image)
        
        tile_width, tile_height, depth = self.grid.tiled_image.shape
        room_height = convert_to_int(self.room_dimensions[0])
        room_width  = convert_to_int(self.room_dimensions[1])
        self.tiled_view_scale = min(tile_height/room_height, tile_width/room_width)
        self.tiled_view_scale = self.tiled_view_scale/2.0

        # update the size of the tiled_view space
        resize_dims = [int(i*self.tiled_view_scale) for i in self.tiled_view_px_dimensions]
        tiled_image.thumbnail(resize_dims, Image.LANCZOS)
        # tiled_image = tiled_image.resize(resize_dims)
        imagetk = ImageTk.PhotoImage(tiled_image)

        w, h   = self.tiled_view_px_dimensions
        for i in range(0, w, resize_dims[0]):
          for j in range(0, h, resize_dims[1]):
            imageid = self.tiled_canvas.create_image(i, j,
                                        anchor='nw', image=imagetk)
        
        self.tiled_canvas.lower(imageid)    # set image into background
        self.tiled_canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

    def save_tiled_view(self, filepath):
        tiled_image = Image.fromarray(self.grid.tiled_image)
        bg_w, bg_h = tiled_image.size
        num_repeats = 1.0/self.tiled_view_scale
        
        new_im = Image.new('RGB', (int(num_repeats*bg_w), int(num_repeats*bg_h)))
        w, h = new_im.size
        for i in range(0, w, bg_w):
            for j in range(0, h, bg_h):
                new_im.paste(tiled_image, (i, j))
        new_im.thumbnail((1080, 720), Image.LANCZOS)
        new_im.save(filepath)
      
    def play(self):
        self.event_loop()

    def save_ptg(self, file_path):
      with open(file_path, 'wb') as outp:
        pickle.dump(self.tileParams, outp, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.grid.image, outp, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.room_dimensions, outp, pickle.HIGHEST_PROTOCOL)
      
    def load_ptg(self, file_path):
      with open(file_path, 'rb') as inp:
        # DO NOT CHANGE ORDER
        self.tileParams = pickle.load(inp)
        grid_image = pickle.load(inp)
        self.room_dimensions = pickle.load(inp)
        
        self.load_image_to_canvas(grid_image_arr=grid_image)
        self.update_window_from_tileparams(new_load=True)
        self.update_titled_view(grid_image)
    
    def update_window_from_tileparams(self, new_load=False):
        if new_load is True:
          self.window['-GROUTING_SIZE-'].Update(self.tileParams.GROUTING_SIZE)
          self.window['-ROOM_HEIGHT-' ].Update(self.room_dimensions[0])
          self.window['-ROOM_WIDTH-' ].Update(self.room_dimensions[1])
        self.update_unit_options_en_disable(self.tileParams.mode, new_load)
        self.window['-TILE_WIDTH-' ].Update(self.tileParams.NEW_TILE_PX_WIDTH //self.tileParams.PIXELS_PER_MM)
        self.window['-TILE_HEIGHT-'].Update(self.tileParams.NEW_TILE_PX_HEIGHT//self.tileParams.PIXELS_PER_MM)

        if self.tileParams.NEW_TILE_PX_WIDTH != self.tileParams.NEW_TILE_PX_HEIGHT:
          self.window['-TILED_Rotated-'].Update(disabled=True)
          self.tiled_view_mode = '-TILED_Mirrored-'
          self.window['-TILED_Mirrored-'].Update(True)
          self.view_rotated_view_options = False
          self.window['-TILED_Rotated_options-'].update(visible=self.view_rotated_view_options)
        else:
          self.window['-TILED_Rotated-'].Update(disabled=False)

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
    from datetime import datetime
    present   = datetime.now()
    LOCK_DATE = datetime(2022, 6, 11)
    if present > LOCK_DATE:
      sg.popup('Completed running', 'Demo expired')
    else:
      game = App()
      game.play()
      sg.popup('Completed running.', 'Click OK to exit the program')
      game.window.close()
