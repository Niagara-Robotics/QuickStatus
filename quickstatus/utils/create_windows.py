from quickstatus.utils.imports import *
from quickstatus.utils.generic import config, copyConfig
from quickstatus.widgets.tab import TabWidget

from os.path import abspath
from os import listdir
from pynput import keyboard

class WindowCreator(QMainWindow):
    def __init__(self):
        super(WindowCreator, self).__init__()

        # create windows
        for file in listdir('resources/fonts'):
            QFontDatabase.addApplicationFont(abspath(f'resources/fonts/{file}'))
        
        self.windowNum = 0
        self.widgets = []

        for window_data in config['window']:
            window = window_data['widget']
            widget = TabWidget(
                wid = self.windowNum,
                conf = copyConfig('tabs', window_data),
                tabs = window.copy()
            )
            self.widgets.append(widget)

            if window_data.get('enabled', True):
                widget.show()
                
            self.windowNum += 1
        
        # start recieving global input
        def sendKeys(key):
            for widget in self.widgets:
                if isinstance(widget, TabWidget): widget.on_press(key)

        self.listener = keyboard.Listener(on_press=sendKeys)
        self.listener.start()