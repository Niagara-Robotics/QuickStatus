from quickstatus.utils.imports import *
from quickstatus.utils.generic import widget_refresh, colours, noNetworkTable, global_font
from quickstatus.utils.network_tables import datatable, NetworkTables
from math import ceil

class InfoBar(QWidget):
        
    def __init__(self, name):
        super(InfoBar, self).__init__()
        #self.config = conf
        self.width_cache = self.width()
        self.height_cache = self.height()
        self.name = name
    
    def resizeEvent(self, event):
        self.width_cache = self.width()
        self.height_cache = self.height()
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        
        #qp.fillRect(QRect(0,0,self.width_cache,self.height_cache), colours.accent_colour)
        font = QFont(global_font)
        font.setPixelSize(15)
        qp.setFont(font)
        qp.setPen(foreground_colour)
        text = 'Widget name: '
        w = QFontMetrics(font).horizontalAdvance(text)
        qp.drawText(QRect(10,0,self.width_cache,self.height_cache), Qt.AlignmentFlag.AlignVCenter, text)
        qp.setPen(colours.death_colour)
        qp.drawText(QRect(10+w,0,self.width_cache,self.height_cache), Qt.AlignmentFlag.AlignVCenter, self.name)

    def setup_palette(self):
        global foreground_colour, background_colour
        palette = self.palette()
        background_colour = QPalette().color(QPalette().ColorRole.Window)
        foreground_colour = palette.color(palette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        if sys.platform == 'darwin': palette.setColor(QPalette.ColorRole.Window, dark)
        self.setPalette(palette)
        self.colour_chart = [foreground_colour, colours.accent_colour, colours.caution_colour, colours.warning_colour, colours.death_colour]