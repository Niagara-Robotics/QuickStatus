from quickstatus.widgets.status import StatusWidget
from quickstatus.utils.imports import *
from quickstatus.utils.generic import restoreWindow, closeEvent

class StatusScrollWidget(QWidget):
    def __init__(self, wid, conf):
        super(StatusScrollWidget, self).__init__()
        #create window with status lights
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))

        restoreWindow(self)

        self.setWindowTitle('QuickStatus (Status Lights)')
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        scroll = QScrollArea(widgetResizable=True)
        scroll.setWidget(StatusWidget(conf))
        layout.addWidget(scroll, 0, 0)
        self.setLayout(layout)
        self.setStyleSheet(
            '''
            background: transparent;
            QScrollArea {
                border: 0px;
            }
            ''')

    def closeEvent(self, e):
        closeEvent(self, e)