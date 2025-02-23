from common import *
from status_scroll_widget import StatusScrollWidget
from swerve_widget import SwerveWidget
from claw_widget import ClawWidget
from tab_widget import TabWidget

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
                if widget == 'claw': self.widgets.append(ClawWidget(wid = self.windowNum))

            if len(self.widgets): self.widgets[-1].show()
            self.windowNum += 1
        
        # start recieving global inputd
        def sendKeys(key):
            for i in range(self.windowNum):
                if isinstance(self.widgets[i], TabWidget): self.widgets[i].on_press(key)

        self.listener = keyboard.Listener(on_press=sendKeys)
        self.listener.start()