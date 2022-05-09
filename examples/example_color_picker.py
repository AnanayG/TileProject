import PySimpleGUI as sg

layout = [[sg.In("", visible=False, enable_events=True, key='set_line_color'),
           sg.ColorChooserButton("", size=(1, 1), target='set_line_color', button_color=('#1f77b4', '#1f77b4'),
                                 border_width=1, key='set_line_color_chooser')],
          [sg.Submit(key='submit')]]

window = sg.Window('Window Title', layout)

while True:
    event, values = window.read()

    if event is None:
        break

    elif event == 'set_line_color':
        window['set_line_color_chooser'].Update(button_color=(values[event], values[event]))

    elif event == 'submit':
        break

window.close()