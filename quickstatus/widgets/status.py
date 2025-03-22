from quickstatus.utils.imports import *
from quickstatus.utils.generic import widget_refresh, colours, noNetworkTable, global_font
from quickstatus.utils.network_tables import datatable, NetworkTables
from math import ceil

class StatusWidget(QWidget):
        
    def __init__(self, conf):
        super(StatusWidget, self).__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.config = conf
        self.width_cache = self.width()
        self.height_cache = self.height()

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

        blink_speed = self.config['blink-interval']
        time = monotonic()

        b = 0

        table = datatable[self.config['network-table']]

        if NetworkTables.inst.isConnected():
            self.radius = 16

            # draw empty slots
            for i in range(ceil(self.height_cache/27)):
                if self.height_cache > (i*27)+12: self.draw_slot(qp, i)

            # draw statuses
            for i in table:
                status = table[i]
                if type(status) == int and status <= 4:
                    self.x = 20
                    self.y = (b * 27) + 12

                    flash_time = time if status != 4 else blink_speed * 2
                    self.current_colour = self.colour_chart[status]
                    self.is_flashing = time % flash_time <= flash_time / 2
                    
                    self.draw_highlight(qp, table, i, b)
                    self.draw_indicator(qp, status)
                    self.draw_text(qp, status, i)
                    
                    b += 1

            self.setMinimumHeight(b*27 + 12)
        else: noNetworkTable(self)

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

    def draw_slot(self, qp:QPainter, i:str):
        width = self.width_cache
        radius = 16
        y = (i * 27) + 12
        qp.setPen(Qt.PenStyle.NoPen)
        if i % 2 == 0: 
            qp.setBrush(Qt.BrushStyle.NoBrush)
        else:
            qp.setBrush(background_colour)
        r1 = QRectF(12, y-5, width-24, radius + 9)
        qp.drawRoundedRect(r1, 6, 6)

    def draw_highlight(self, qp:QPainter, table:dict, i:str, b:int):
        width = self.width_cache
        qp.setPen(Qt.PenStyle.NoPen)
        qp.setBrush(Qt.BrushStyle.NoBrush)

        if b <= len(table) and (table[i] != 0) and self.is_flashing:
            if b % 2 == 0: qp.setBrush(self.current_colour.darker(110))
            else: qp.setBrush(self.current_colour)

        qp.drawRoundedRect(QRectF(12, self.y-5, width-24, self.radius + 9), 6, 6)

    def draw_indicator(self, qp:QPainter, status:int):
        qp.setPen(QPen(foreground_colour, 1.5))

        if status != 0: 
            qp.setBrush(self.current_colour)
            if self.is_flashing: qp.setPen(QPen(QColor('#FFFFFF'), 1.5))
            else: qp.setPen(QPen(foreground_colour, 1.5))
        else: qp.setBrush(Qt.BrushStyle.NoBrush)

        qp.drawEllipse(QRectF(self.x, self.y-1, self.radius, self.radius))

    def draw_text(self, qp:QPainter, status:int, i:str):
        # setup variables
        width = self.width_cache
        text = i
        text_x = self.x + self.radius + 6
        text_y = self.y+13
        font = QFont(global_font)
        font.setPixelSize(15)
        qp.setFont(font)
        if status != 0 and self.is_flashing: qp.setPen(QColor('#FFFFFF'))
        else: qp.setPen(foreground_colour)
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.horizontalAdvance(text)

        # shorten offscreen text
        if text_width > width-45:
            truncated_text = font_metrics.elidedText(text, Qt.TextElideMode.ElideRight, width-45)
            qp.drawText(text_x, text_y, truncated_text)
        else:
            qp.drawText(text_x, text_y, text)