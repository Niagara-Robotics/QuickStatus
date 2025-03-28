from quickstatus.utils.imports import *
from quickstatus.utils.generic import widget_refresh, Colours, noNetworkTable, global_config
from quickstatus.utils.network_tables import datatable, NetworkTables

class FaultWidget(QWidget):
        
    def __init__(self, conf):
        super(FaultWidget, self).__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.config = conf
        self.width_cache = self.width()
        self.height_cache = self.height()

        self.global_font = global_config.data['general']['global_font']

    # scrolling setup
    def minimumSizeHint(self):
        if self.config['enable-scroll']: minY = self.height_cache
        else: minY = 0

        return QSize(0, minY)
    
    def resizeEvent(self, event):
        self.width_cache = self.width()
        self.height_cache = self.height()
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨

        time = monotonic()

        b = 0

        table = datatable[self.config['network-table']]

        if NetworkTables.inst.isConnected():
            # variables
            self.y = 12
            self.radius = 16
            self.title_size = 28
            self.text_size = 16
            self.line_spacing = 8
            self.empty_space = self.line_spacing
            self.swap = 0

            # create categories
            for category in self.config['fault_list']:
                title = category['name']
                self.check_data(table, category)

                if self.faults is not None:
                    self.empty = not self.faults

                    if not (self.config['hide-if-empty'] and self.empty):
                        self.x = 24

                        self.draw_slot(qp)
                        self.draw_title(qp, title, self.title_size, 12)
                        self.x += 24

                        self.draw_faults(qp)
                        
                        self.y += self.text_size
                        self.swap += 1

            self.setMinimumHeight(self.y)
        else: noNetworkTable(self)
    
    def check_data(self, table:dict, category:dict):
        try: self.faults = table[category['fault']]
        except: self.faults = None

    def setup_palette(self):
        palette = self.palette()
        new_palette = QPalette()
        self.background_colour = new_palette.color(new_palette.ColorRole.Window)
        self.foreground_colour = palette.color(palette.ColorRole.Text)
        self.foreground_colour.setAlpha(255)
        self.translucent_colour = palette.color(palette.ColorRole.Text)
        self.translucent_colour.setAlpha(120)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        if sys.platform == 'darwin': palette.setColor(QPalette.ColorRole.Window, dark)
        self.setPalette(palette)
        self.colour_chart = [self.foreground_colour, Colours.accent_colour, Colours.caution_colour, Colours.warning_colour, Colours.death_colour]

    def draw_slot(self, qp:QPainter):
        total_height = self.title_size+12+(len(self.faults)*(self.text_size+self.line_spacing*3))
        if self.empty: self.empty_space = self.line_spacing
        else: self.empty_space = 0

        if self.swap % 2: 
            qp.setPen(Qt.PenStyle.NoPen)
            qp.setBrush(self.background_colour)
            qp.drawRoundedRect(QRect(12, self.y-self.line_spacing, self.width_cache-24,total_height+self.empty_space), 8,8)
    
    def draw_title(self, qp:QPainter, title:str, size:int, line_height:int):
        # setup variables
        width = self.width_cache
        text_x = self.x
        text_y = self.y
        font = QFont(self.global_font)
        font.setBold(True)
        font.setPixelSize(size)
        font_met = QFontMetrics(font)
        qp.setFont(font)
        text_height = QFontMetrics(font).height()

        title = font_met.elidedText(title, Qt.TextElideMode.ElideRight, width-48)

        if self.empty: qp.setPen(self.translucent_colour)
        else: qp.setPen(self.foreground_colour)
        qp.drawText(QRect(text_x,text_y,width, text_height), Qt.AlignmentFlag.AlignVCenter, title)
        self.y += size+line_height

    def draw_faults(self, qp:QPainter):
        indent_y = self.y
        if not self.empty:
            for fault in self.faults:
                self.draw_text(qp, fault['text'], self.text_size, self.line_spacing)

            qp.setPen(QPen(self.foreground_colour, 4, cap=Qt.PenCapStyle.RoundCap))
            line_x = int(self.x/1.5)
            # draw line
            qp.drawLine(line_x, indent_y, line_x, self.y-self.line_spacing)
            self.y += self.line_spacing
    
    def draw_text(self, qp:QPainter, text:str, size:int, line_height:int):
        # setup variables
        width = self.width_cache
        text_x = self.x
        text_y = self.y
        font = QFont(self.global_font)
        font.setPixelSize(size)
        qp.setFont(font)
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.horizontalAdvance(text)
        text_height = font_metrics.height()

        # shorten offscreen text
        truncated_text = font_metrics.elidedText(text, Qt.TextElideMode.ElideRight, width-64)
        
        qp.drawText(QRect(text_x, text_y, text_width, text_height), Qt.AlignmentFlag.AlignVCenter, truncated_text)
        self.y += size+line_height