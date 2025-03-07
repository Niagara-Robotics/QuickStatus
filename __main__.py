from quickstatus.utils.imports import *
from quickstatus.utils.create_windows import WindowCreator
from quickstatus.utils.network_tables import NetworkTables

if __name__ == '__main__':
    # pyqt stuff
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('resources/icons/mac.png'))
    if sys.platform == 'win32': app.setStyle('Fusion')
    ex = WindowCreator()
    NetworkTables()
    app.exec()
    sys.exit()