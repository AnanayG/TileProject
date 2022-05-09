import PySimpleGUI as sg

layout = [[sg.Button('Line01'), sg.VerticalSeparator(), sg.Button('Line02')],
          [sg.VerticalSeparator()],    # Not use this
          [sg.Button('Line02')],
          [sg.Text()],
          [sg.Button('Line03')]]

window = sg.Window('Test', layout)
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
window.close()