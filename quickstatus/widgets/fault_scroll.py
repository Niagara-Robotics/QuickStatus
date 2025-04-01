from quickstatus.widgets.faults import FaultWidget
from quickstatus.utils.imports import *
from quickstatus.utils.generic import restoreWindow

class FaultScrollWidget(QWidget):
    name = 'Faults'
    def __init__(self, wid, conf):
        super(FaultScrollWidget, self).__init__()

        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        scroll = QScrollArea(widgetResizable=True)
        scroll.setWidget(FaultWidget(self.config))
        layout.addWidget(scroll, 0, 0)
        self.setLayout(layout)

        if sys.platform == 'darwin':
            self.setBackgroundRole(QPalette().ColorRole.Window)
            self.setAutoFillBackground(True)
        else:
            palette = scroll.palette()
            palette.setColor(QPalette.ColorRole.Base, QColor('#00000000'))
            scroll.setPalette(palette)