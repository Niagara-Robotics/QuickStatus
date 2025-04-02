from quickstatus.utils.imports import *
from quickstatus.utils.create_windows import WindowCreator
from quickstatus.utils.network_tables import NetworkTables
from quickstatus.widgets.menu_bar import MenuBar

is_exe = getattr(sys, 'frozen', False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not is_exe: app.setWindowIcon(QIcon('resources/icons/icon.png'))
    elif sys.platform == 'win32': app.setWindowIcon(QIcon(f"{sys._MEIPASS}\\icon.ico"))
    if sys.platform == 'win32': app.setStyle('Fusion')
    if sys.platform == 'darwin': menu_bar = MenuBar()
    ex = WindowCreator()
    NetworkTables()
    app.exec()
    sys.exit()