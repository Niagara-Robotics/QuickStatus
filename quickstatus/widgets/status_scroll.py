from quickstatus.widgets.status import StatusWidget
from quickstatus.utils.imports import *
from quickstatus.utils.generic import restoreWindow

class StatusScrollWidget(QWidget):
    def __init__(self, wid, conf):
        super(StatusScrollWidget, self).__init__()
        #create window with status lights
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))

        restoreWindow(self)

        self.setWindowTitle('Status Lights')
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        scroll = QScrollArea(widgetResizable=True)
        scroll.setWidget(StatusWidget(conf))
        layout.addWidget(scroll, 0, 0)
        self.setLayout(layout)
        self.setBackgroundRole(QPalette().ColorRole.Window)
        self.setAutoFillBackground(True)