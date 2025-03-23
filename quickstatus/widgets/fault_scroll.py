from quickstatus.widgets.faults import FaultWidget
from quickstatus.utils.imports import *
from quickstatus.utils.generic import restoreWindow

class FaultScrollWidget(QWidget):
    name = 'Faults'
    def __init__(self, wid, conf):
        super(FaultScrollWidget, self).__init__()

        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))

        restoreWindow(self)

        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        scroll = QScrollArea(widgetResizable=True)
        scroll.setWidget(FaultWidget(conf))
        layout.addWidget(scroll, 0, 0)
        self.setLayout(layout)
        self.setBackgroundRole(QPalette().ColorRole.Window)
        self.setAutoFillBackground(True)