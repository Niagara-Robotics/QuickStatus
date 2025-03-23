from quickstatus.utils.imports import *
from quickstatus.utils.generic import widget_refresh, Colours, noNetworkTable, global_font, fault_icons
from quickstatus.utils.network_tables import datatable, NetworkTables
from math import ceil

class InfoBar(QWidget):
    def __init__(self, name):
        super(InfoBar, self).__init__()
        #self.config = conf
        self.width_cache = self.width()
        self.height_cache = self.height()
    
    def resizeEvent(self, event):
        self.width_cache = self.width()
        self.height_cache = self.height()
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        
        qp.fillRect(QRect(0,0,self.width_cache,self.height_cache), self.background_colour)
        font = QFont(global_font)
        font.setPixelSize(15)
        qp.setFont(font)
        qp.setPen(self.foreground_colour)
        text = 'Test Icon: '
        w = QFontMetrics(font).horizontalAdvance(text)
        qp.drawText(QRect(10,0,self.width_cache,self.height_cache), Qt.AlignmentFlag.AlignVCenter, text)

        self.draw_icon(qp, QRect(10+w,3,24,24), 'rotation_motor.svg', Colours.warning_colour)

    def setup_palette(self):
        palette = self.palette()
        self.background_colour = palette.color(palette.ColorRole.Base)
        self.foreground_colour = palette.color(palette.ColorRole.Text)
        self.foreground_colour.setAlpha(255)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        if sys.platform == 'darwin': palette.setColor(QPalette.ColorRole.Window, dark)
        self.setPalette(palette)
        self.colour_chart = [self.foreground_colour, Colours.accent_colour, Colours.caution_colour, Colours.warning_colour, Colours.death_colour]
    
    def draw_icon(self, qp:QPainter, rect:QRect, icon:str, colour:QColor):
        icon = fault_icons[icon]
        if icon is not None:
            qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)
            icon.paint(qp,rect)

            qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationAtop)
            qp.fillRect(rect, colour)

            qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)