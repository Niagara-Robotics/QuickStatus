from status_widget import StatusWidget
from common import *

class StatusScrollWidget(QWidget):
    def __init__(self, wid, conf):
        super(StatusScrollWidget, self).__init__()
        #create window with status lights
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))

        restoreWindow(self)

        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        scroll = QScrollArea(widgetResizable=True)
        scroll.setWidget(StatusWidget(conf))
        layout.addWidget(scroll, 0, 0)
        self.setLayout(layout)

        palette = self.palette()
        dark = palette.color(QPalette.ColorRole.Base).lighter(160)
        palette.setColor(QPalette.ColorRole.Window, dark)
        self.setPalette(palette)

        self.setWindowTitle('QuickStatus (Status Indicators)')

    def closeEvent(self, e):
        if config['general']['save-window-states']:
            self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        e.accept()