import PySimpleGUI as sg
from win32api import GetSystemMetrics
from datetime import datetime

BACKGROUND_COLOR = '#262729'
TEXT_COLOR = '#e3e3e4'
BOLD_FONT = 'CM Sans Serif 2012'
REGULAR_FONT = 'Arial Regular'

class AlertBox:

    def __init__(self):
        self.layout = [[sg.Text('Unauthorized Person May Be Looking At Screen', background_color=BACKGROUND_COLOR,
                                text_color=TEXT_COLOR, font=(BOLD_FONT, 12))],
                       [sg.Text('Make sure to check your surroundings', background_color=BACKGROUND_COLOR,
                                text_color=TEXT_COLOR, font=(REGULAR_FONT, 12))]]
        self.window = sg.Window('Window Title', self.layout, no_titlebar=True, finalize=True, keep_on_top=True,
                                default_button_element_size=(500, 1), background_color=BACKGROUND_COLOR)
        self.window.hide()
        self.isHidden = True
        self.screen_width = GetSystemMetrics(0)
        self.screen_height = GetSystemMetrics(1)
        self.window.move(self.screen_width, (self.screen_height - self.window.size[1]) - 100)
        return

    def activate(self):
        self.window.un_hide()
        for i in range(0, self.window.size[0]):
            self.window.move(self.screen_width - i, (self.screen_height - self.window.size[1]) - 100)
            self.window.Refresh()
        self.isHidden = False
        return

    def deactivate(self):
        for i in range(0, self.window.size[0]):
            self.window.move((self.screen_width - self.window.size[0]) + i,
                             (self.screen_height - self.window.size[1]) - 100)
            self.window.Refresh()
        self.window.hide()
        self.isHidden = True
        return

    # def destroy(self):
    #     self.window.close
    #     return
