from utils.imports import *
from utils.generic import config, copyConfig
from widgets.status_scroll import StatusScrollWidget
from widgets.swerve import SwerveWidget
from widgets.lift import LiftWidget
from widgets.tab import TabWidget
from widgets.intake import IntakeWidget

from pynput import keyboard

class WindowCreator(QMainWindow):
    def __init__(self):
        super(WindowCreator, self).__init__()

        # create windows
        self.windowNum = 0
        self.widgets = []
        for i in range(len(config['window'])):
            window = config['window'][i]['widget']
            if len(window) > 1:
                self.widgets.append(TabWidget(wid=self.windowNum, conf = copyConfig('tabs', config['window'][i]), tabs = window.copy()))
            else:
                widget = window[0]['type']
                if widget == 'status': self.widgets.append(StatusScrollWidget(wid = self.windowNum, conf = copyConfig('status', window[0])))
                if widget == 'swerve': self.widgets.append(SwerveWidget(wid = self.windowNum, conf = copyConfig('swerve', window[0])))
                if widget == 'lift': self.widgets.append(LiftWidget(wid = self.windowNum, conf = copyConfig('lift', window[0])))
                if widget == 'intake': self.widgets.append(IntakeWidget(wid = self.windowNum, conf = copyConfig('intake', window[0])))

            if len(self.widgets): self.widgets[-1].show()
            self.windowNum += 1
        
        # start recieving global inputd
        def sendKeys(key):
            for i in range(self.windowNum):
                if isinstance(self.widgets[i], TabWidget): self.widgets[i].on_press(key)

        self.listener = keyboard.Listener(on_press=sendKeys)
        self.listener.start()