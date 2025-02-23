# config
import sys, os
from shutil import copyfile

def resource_path(relative_path):
    # absolute file paths
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

try:
    config = open(resource_path("resources/config.toml"))
    config.close()
except:
    print("No config file found, creating one automatically")
    copyfile(resource_path("resources/assets/default.toml"), resource_path('resources/config.toml'))

# start app
from common import *
config = getConfig()
from create_windows import WindowCreator

if __name__ == '__main__':
    # pyqt stuff
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('resources/assets/icon/mac.png')))
    if sys.platform == 'win32': app.setStyle('Fusion')
    ex = WindowCreator()
    sys.exit(app.exec())