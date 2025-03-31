from quickstatus.utils.imports import *
from subprocess import run

class MenuBar(QMenuBar):
    """A macOS global menu bar that works without QMainWindow."""
    def __init__(self):
        super().__init__()

        file_menu = self.addMenu("File")
        open_config = QAction("Open Config", self)
        open_config.triggered.connect(self.open_config)
        file_menu.addActions([open_config])
    
    def open_config(self):
        run(['open', 'resources/config.toml'])