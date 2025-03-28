from quickstatus.utils.imports import *
from quickstatus.utils.generic import widget_refresh, Colours, fault_icons, global_config
from quickstatus.utils.network_tables import datatable, NetworkTables

class InfoBar(QWidget):
    def __init__(self, faults):
        super(InfoBar, self).__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.width_cache = self.width()
        self.height_cache = self.height()
        self.faults = faults

        self.global_font = global_config.data['general']['global_font']
    
    def resizeEvent(self, event):
        self.width_cache = self.width()
        self.height_cache = self.height()
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        
        qp.fillRect(QRect(0,0,self.width_cache,self.height_cache), self.background_colour)
        font = QFont(self.global_font)
        font.setPixelSize(15)
        qp.setFont(font)
        qp.setPen(self.foreground_colour)
        text = 'NetworkTable not connected'
        w = 0

        table = datatable.get(global_config.data['faults']['network-table'], {})
        if table.get(self.faults[0], []): bg = Colours.death_colour
        else: bg = Colours.accent_colour

        # draw faults
        if not NetworkTables.inst.isConnected():
            qp.fillRect(QRect(0,0,self.width_cache,self.height_cache), self.background_colour)
        else:
            qp.fillRect(QRect(0,0,self.width_cache,self.height_cache), bg)
            for fault in self.faults:
                fault_entries = table.get(fault, [])
                
                if fault_entries:
                    for k in fault_entries:
                        if k.get('icon') in fault_icons:
                            self.draw_icon(qp, QRect(10+w, 1, 28, 28), k['icon'], self.foreground_colour)
                            w += 30
                else:
                    text = 'No faults'

        # fallback text
        if w == 0:
            w = QFontMetrics(font).horizontalAdvance(text)
            qp.drawText(QRect(10, 0, self.width_cache, self.height_cache), Qt.AlignmentFlag.AlignVCenter, text)
        
        # draw divider
        qp.setPen(QPen(self.hl, 1))
        qp.drawLine(0,0,self.width_cache,0)

    def setup_palette(self):
        palette = self.palette()
        self.background_colour = palette.color(palette.ColorRole.Base)
        self.foreground_colour = palette.color(palette.ColorRole.Text)
        self.foreground_colour.setAlpha(255)
        self.hl = palette.color(palette.ColorRole.WindowText)
        self.hl.setAlpha(70)
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