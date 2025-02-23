import sys, os, toml
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel

config = {}

accent_colour = QColor("#0779FF")
caution_colour = QColor("#FFC600")
warning_colour = QColor("#F7821B")
death_colour = QColor("#FF5257")
velocity_colour = QColor("#60DE36")
power_colour = QColor("#47AC25")

refresh = 10

def resource_path(relative_path):
    # absolute file paths
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def getConfig():
    with open(resource_path('resources/config.toml'), 'r') as f:
        return(toml.load(f))
config = getConfig()

def copyConfig(original: str, copyto: dict):
    config = getConfig()
    new = copyto.copy()
    for i in config[original]:
        if not i in new: new[i] = config[original][i]
    new.pop('type', None)
    return new

def restoreWindow(self):
    config = getConfig()
    windowScreenGeometry = self.settings.value("windowScreenGeometry")
    if windowScreenGeometry and config['general']['save-window-states']:
            self.restoreGeometry(windowScreenGeometry)
    else:
        self.resize(640, 480)