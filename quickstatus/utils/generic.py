from utils.imports import *

widget_refresh = 10

class colours():
    accent_colour = QColor("#0779FF")
    caution_colour = QColor("#FFC600")
    warning_colour = QColor("#F7821B")
    death_colour = QColor("#FF5257")
    velocity_colour = QColor("#60DE36")
    power_colour = QColor("#47AC25")

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
    config = getConfig()
    windowScreenGeometry = self.settings.value("windowScreenGeometry")
    if windowScreenGeometry and config['general']['save-window-states']:
            self.restoreGeometry(windowScreenGeometry)
    else:
        self.resize(640, 480)