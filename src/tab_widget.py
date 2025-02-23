from common import *
from status_scroll_widget import StatusScrollWidget
from swerve_widget import SwerveWidget
from claw_widget import ClawWidget

class TabWidget(QWidget):
    def __init__(self, wid, conf, tabs):
        super(TabWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf
        self.tablist = tabs

        restoreWindow(self)

        # create tab widget
        widget = QWidget()
        self.layout = QGridLayout(widget)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(getattr(self.tabs.TabPosition, self.config['align']))

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
            if i['type'] == 'claw': self.claw_tab()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.setWindowTitle('QuickStatus (Tabs)')

        selectedTab = self.settings.value("selectedTab")
        if selectedTab and config['general']['save-window-states']:
            self.tabs.setCurrentIndex(selectedTab)
    def on_press(self, key):
        if self.config['global-hotkeys'] and hasattr(key, 'char') and key.char.isnumeric():
            key_text = (int(key.char)-1) % 10
            self.tabs.setCurrentIndex(key_text)

    def status_tab(self, conf):
        self.tabs.addTab(StatusScrollWidget(wid = self.wid, conf = conf), "Status Lights")

    def swerve_tab(self, conf):
        self.tabs.addTab(SwerveWidget(wid = self.wid, conf = conf), "Swerve State")

    def claw_tab(self):
        self.tabs.addTab(ClawWidget(wid = self.wid), "Claw State")

    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent) and not self.config['global-hotkeys']:
            key_text = event.text()
            if key_text.isnumeric():
                key_text = (int(key_text)-1) % 10
                self.tabs.setCurrentIndex(key_text)

    def changeEvent(self, e):
        hl = self.palette().color(QPalette.ColorRole.WindowText)
        hl = hl.name().strip('#')
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
                border-{alignment}: 1px solid;
                border-color: #25{hl};
                margin-{alignment}: 5px;
            }}
            """)
        else:
            self.tabs.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border-{alignment}: 1px solid;
                border-color: #25{hl};
            }}
            """)

    def closeEvent(self, e):
        if config['general']['save-window-states']:
            self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
            self.settings.setValue( "selectedTab", self.tabs.currentIndex() )
        e.accept()