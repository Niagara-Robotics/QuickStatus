from quickstatus.utils.imports import *
from quickstatus.utils.generic import config, copyConfig
from quickstatus.widgets.status_scroll import StatusScrollWidget
from quickstatus.widgets.swerve import SwerveWidget
from quickstatus.widgets.lift import LiftWidget
from quickstatus.widgets.tab import TabWidget
from quickstatus.widgets.intake import IntakeWidget

from os.path import abspath
from pynput import keyboard

class WindowCreator(QMainWindow):
    def __init__(self):
        super(WindowCreator, self).__init__()

        # create windows
        QFontDatabase.addApplicationFont(abspath('resources/fonts/IosevkaAile-Regular.ttf'))
        self.windowNum = 0
        self.widgets = []
        for i in range(len(config['window'])):
            window = config['window'][i]['widget']
            self.widgets.append(TabWidget(wid=self.windowNum, conf = copyConfig('tabs', config['window'][i]), tabs = window.copy()))

            if len(self.widgets) and (('enabled' in config['window'][i] and config['window'][i]['enabled']) or 'enabled' not in config['window'][i]): self.widgets[-1].show()
            self.windowNum += 1
        
        # start recieving global inputd
        def sendKeys(key):
            for i in range(self.windowNum):
                if isinstance(self.widgets[i], TabWidget): self.widgets[i].on_press(key)

        self.listener = keyboard.Listener(on_press=sendKeys)
        self.listener.start()