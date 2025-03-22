from quickstatus.utils.imports import *
from quickstatus.utils.generic import restoreWindow, copyConfig, config, closeEvent
from quickstatus.widgets.status_scroll import StatusScrollWidget
from quickstatus.widgets.swerve import SwerveWidget
from quickstatus.widgets.lift import LiftWidget
from quickstatus.widgets.intake import IntakeWidget
from quickstatus.widgets.reef import ReefWidget
from quickstatus.widgets.info_bar import InfoBar

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
        self.tabs.setLayout(QGridLayout())
        self.tabs.setTabPosition(getattr(self.tabs.TabPosition, self.config['align']))
        self.tabs.setTabBarAutoHide(True)
        self.visible = len(self.tablist) > 1
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
        if not self.visible: self.layout.setContentsMargins(0,0,0,0)
        
        # create tabs
        for i in self.tablist:
            if i['type'] == 'status': self.status_tab(conf = copyConfig('status', i))
            if i['type'] == 'swerve': self.swerve_tab(conf = copyConfig('swerve', i))
            if i['type'] == 'lift': self.lift_tab(conf = copyConfig('lift', i))
            if i['type'] == 'intake': self.intake_tab(conf = copyConfig('intake', i))
            if i['type'] == 'reef': self.reef_tab(conf = copyConfig('reef', i))
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.setWindowTitle('QuickStatus (Tabs)')
        if not self.visible: self.setWindowTitle(f"QuickStatus({self.tabs.currentWidget().windowTitle()})")

        selectedTab = self.settings.value("selectedTab")
        if selectedTab and config['general']['save-window-states']:
            self.tabs.setCurrentIndex(int(selectedTab))
        
        restoreWindow(self)

    def on_press(self, key):
        if self.config['global-hotkeys'] and hasattr(key, 'char') and hasattr(key.char, 'isnumeric') and  key.char.isnumeric():
            key_text = (int(key.char)-1) % 10
            self.tabs.setCurrentIndex(key_text)
    def stack_widgets(self, top, bottom):
        title = top.windowTitle()
        stack = QWidget()
        stack.setLayout(QGridLayout())
        stack.layout().setContentsMargins(0,0,0,0)
        stack.layout().setSpacing(0)
        bottom = bottom(title)
        bottom.setFixedHeight(30)
        stack.layout().addWidget(top, 0,0,1,1)
        stack.layout().addWidget(bottom, 1,0,1,1)

        self.tabs.addTab(stack, top.windowTitle())

    def status_tab(self, conf):
        self.stack_widgets(StatusScrollWidget(wid = self.wid, conf = conf), InfoBar)

    def swerve_tab(self, conf):
        self.stack_widgets(SwerveWidget(wid = self.wid, conf = conf), InfoBar)

    def lift_tab(self, conf):
        self.stack_widgets(LiftWidget(wid = self.wid, conf = conf), InfoBar)
        
    def intake_tab(self, conf):
        self.stack_widgets(IntakeWidget(wid = self.wid, conf = conf), InfoBar)

    def reef_tab(self, conf):
        self.stack_widgets(ReefWidget(wid = self.wid, conf = conf), InfoBar)

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
                border-{alignment}: {1*self.visible}px solid;
                border-color: #26{hl};
                margin-{alignment}: {5*self.visible}px;
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