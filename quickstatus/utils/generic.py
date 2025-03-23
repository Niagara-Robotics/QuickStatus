from quickstatus.utils.imports import *
import toml
import json
import os.path

class Colours():
    accent_colour = QColor("#0779FF")
    caution_colour = QColor("#FFC600")
    warning_colour = QColor("#F7821B")
    death_colour = QColor("#FF5257")
    velocity_colour = QColor("#60DE36")
    power_colour = QColor("#47AC25")

class FaultCache():
    with open('resources/widgets/faults/identifiers.json') as file:
        faults = json.load(file)
        full_faults = {}
        fault_icons = {}
        for fault in faults:
            full_faults[str(fault)] = faults[fault]
            icon = faults[fault]['icon']
            file = f'resources/widgets/faults/icons/{icon}'
            if os.path.isfile(file): fault_icons[icon] = QIcon(file)
            else: fault_icons[icon] = None

def getConfig():
    with open('resources/config.toml', 'r') as f:
        return(toml.load(f))
config = getConfig()

def copyConfig(original: str, copyto: dict):
    config = getConfig()
    new = copyto.copy()
    for i in config[original]:
        if not i in new: new[i] = config[original][i]
    new.pop('type', None)
    return new

def closeEvent(self, e):
    if config['general']['save-window-states']:
        self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        if hasattr(self, 'tabs'): self.settings.setValue( "selectedTab", self.tabs.currentIndex() )
    e.accept()

def restoreWindow(self):
    windowScreenGeometry = self.settings.value("windowScreenGeometry")
    if windowScreenGeometry and config['general']['save-window-states']:
        self.restoreGeometry(windowScreenGeometry)
    else:
        self.resize(640, 480)

def noNetworkTable(self):
    qp = QPainter(self)
    width = self.size().width()
    height = self.size().height()
    palette = self.palette()
    self.foreground_colour = palette.color(palette.ColorRole.Text)
    self.foreground_colour.setAlpha(255)
    qp.setPen(self.foreground_colour)
    font = QFont('Iosevka Aile')
    font.setPixelSize(24)
    qp.setFont(font)
    text = "NetworkTable not connected"
    font_metrics = QFontMetrics(font)
    text_width = font_metrics.horizontalAdvance(text)/2
    text_height = font_metrics.height()
    qp.drawText(QPointF(width/2-text_width, height/2+text_height/4), text)
    self.setMinimumHeight(text_height)

widget_refresh = 10
global_font = config['general']['global_font']
full_faults = FaultCache.full_faults
fault_icons = FaultCache.fault_icons