from utils.imports import *
from create_windows import WindowCreator

if __name__ == '__main__':
    # pyqt stuff
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('resources/icons/mac.png'))
    if sys.platform == 'win32': app.setStyle('Fusion')
    ex = WindowCreator()
    sys.exit(app.exec())