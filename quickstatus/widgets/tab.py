from utils.imports import *
from utils.generic import restoreWindow, copyConfig, config, closeEvent
from widgets.status_scroll import StatusScrollWidget
from widgets.swerve import SwerveWidget
from widgets.lift import LiftWidget
from widgets.intake import IntakeWidget

class TabWidget(QWidget):
    def __init__(self, wid, conf, tabs):
        super(TabWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf
        self.tablist = tabs

        # create tab widget
        widget = QWidget()
        self.layout = QGridLayout(widget)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(getattr(self.tabs.TabPosition, self.config['align']))
        self.setBackgroundRole(QPalette().ColorRole.Base)
        self.setAutoFillBackground(True)

        margins = {
            'North': [0,11,0,0],
            'East': [0,0,6,0],
            'South': [0,0,0,6],
            'West': [6,0,0,0]
        }
        margin = margins.get(self.config['align'])
        self.layout.setContentsMargins(margin[0], margin[1], margin[2], margin[3])
        
        # create tabs
        for i in self.tablist:
            if i['type'] == 'status': self.status_tab(conf = copyConfig('status', i))
            if i['type'] == 'swerve': self.swerve_tab(conf = copyConfig('swerve', i))
            if i['type'] == 'lift': self.lift_tab(conf = copyConfig('lift', i))
            if i['type'] == 'intake': self.intake_tab(conf = copyConfig('intake', i))
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.setWindowTitle('QuickStatus (Tabs)')

        selectedTab = self.settings.value("selectedTab")
        if selectedTab and config['general']['save-window-states']:
            self.tabs.setCurrentIndex(selectedTab)
        
        restoreWindow(self)

    def on_press(self, key):
        if self.config['global-hotkeys'] and hasattr(key, 'char') and hasattr(key.char, 'isnumeric') and  key.char.isnumeric():
            key_text = (int(key.char)-1) % 10
            self.tabs.setCurrentIndex(key_text)

    def status_tab(self, conf):
        self.tabs.addTab(StatusScrollWidget(wid = self.wid, conf = conf), "Status Lights")

    def swerve_tab(self, conf):
        self.tabs.addTab(SwerveWidget(wid = self.wid, conf = conf), "Swerve State")

    def lift_tab(self, conf):
        self.tabs.addTab(LiftWidget(wid = self.wid, conf = conf), "Lift State")
        
    def intake_tab(self, conf):
        self.tabs.addTab(IntakeWidget(wid = self.wid, conf = conf), "Intake")

    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent) and not self.config['global-hotkeys']:
            key_text = event.text()
            if key_text.isnumeric():
                key_text = (int(key_text)-1) % 10
                self.tabs.setCurrentIndex(key_text)

    def changeEvent(self, e):
        pal = self.palette()
        pal.setColor(self.palette().ColorRole.Window, self.palette().color(self.palette().ColorRole.Light).darker(115))
        self.setPalette(pal)
        hl = self.palette().color(self.palette().ColorRole.WindowText)
        hl = hl.name().strip('#')
        bg = QPalette().color(QPalette().ColorRole.Window)
        if sys.platform == 'darwin': bg = self.palette().color(self.palette().ColorRole.Base).lighter(160)
        bg = bg.name()
        align_css = {
            'North': 'top',
            'East': 'right',
            'South': 'bottom',
            'West': 'left'
        }
        alignment = align_css.get(self.config['align'])
        if sys.platform == "darwin":
            self.tabs.setStyleSheet(
            f"""
            QTabWidget::pane {{
                background-color: {bg};
                border-{alignment}: 1px solid;
                border-color: #26{hl};
                margin-{alignment}: 5px;
            }}
            """)
        else:
            palette = self.tabs.palette()
            background_colour = QPalette().color(QPalette().ColorRole.Window).darker(120)
            palette.setColor(QPalette.ColorRole.Button, background_colour)
            palette.setColor(QPalette.ColorRole.Window, background_colour)

            self.tabs.setPalette(palette)

    def closeEvent(self, e):
        closeEvent(self, e)