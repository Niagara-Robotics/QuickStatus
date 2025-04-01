from quickstatus.utils.imports import *
from quickstatus.utils.generic import global_config, copyConfig
from quickstatus.widgets.tab import TabWidget
from quickstatus.widgets.error_popup import ErrorPopup
import quickstatus.utils.generic as generic

from os.path import abspath
from pathlib import Path
from os import listdir
from pynput import keyboard

class WindowCreator(QMainWindow):
    def __init__(self):
        super(WindowCreator, self).__init__()

        error = generic.global_config.load()
        if error: ErrorPopup(error[0], error[1])
        config = global_config.data
        generic.global_font = config['general']['global_font']

        try: Path('resources').resolve(strict=True)
        except Exception as e: ErrorPopup(200, e)
        try: Path('resources/fonts').resolve(strict=True)
        except Exception as e: ErrorPopup(201, e)
        try: Path('resources/widgets').resolve(strict=True)
        except Exception as e: ErrorPopup(202, e)

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
        
        if config['general']['global-hotkeys']:
            self.listener = keyboard.Listener(on_press=sendKeys)
            self.listener.start()