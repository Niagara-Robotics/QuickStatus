from utils.imports import *
from utils.generic import widget_refresh, colours, config
from time import time
from utils.network_tables import datatable, NetworkTables
from math import ceil

start_time = time()

class StatusWidget(QWidget):
        
    def __init__(self, conf):
        super(StatusWidget, self).__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.config = conf

    # scrolling setup
    def minimumSizeHint(self):
        if self.config['enable-scroll'] == False: minY = 0
        else: minY = self.height()

        return QSize(0, minY)
        
    # draw status lights
    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        
        palette = self.palette()
        background_colour = QPalette().color(QPalette().ColorRole.Window)
        foreground_colour = palette.color(palette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        if sys.platform == 'darwin': palette.setColor(QPalette.ColorRole.Window, dark)
        self.setPalette(palette)

        flash_time = 100

        size = self.size()
        width = size.width()
        height = size.height()
        total_width = 0
        blink_speed = self.config['blink-interval']
        ctime = (time() - start_time) # how long the program has been running

        colour_chart = [foreground_colour, colours.accent_colour, colours.caution_colour, colours.warning_colour, colours.death_colour]
        b = 0

        table = datatable[config['status']['network-table']]

        if NetworkTables.inst.isConnected():
            for i in range(ceil(height/27)):
                radius = 16
                y = (i * 27) + 12
                qp.setPen(Qt.PenStyle.NoPen)
                if i % 2 == 0: 
                    qp.setBrush(Qt.BrushStyle.NoBrush)
                else:
                    qp.setBrush(background_colour)
                r1 = QRectF(12, y-5, width-24, radius + 9)
                qp.drawRoundedRect(r1, 6, 6)
            for i in table:
                if type(table[i]) == int:
                    x = 20
                    y = (b * 27) + 12
                    radius = 16

                    pen = QPen(Qt.PenStyle.NoPen)

                    flash_time = ctime
                    current_colour = colour_chart[table[i]]
                    if table[i] == 4 and blink_speed > 0: flash_time = blink_speed*2
                    
                    pen.setStyle(Qt.PenStyle.NoPen)
                    qp.setPen(pen)
                    qp.setBrush(Qt.BrushStyle.NoBrush)
                    if b % 2 == 0: 
                        if b <= len(table) and (table[i] != 0) and (ctime % flash_time) <= flash_time/2: qp.setBrush(current_colour.darker(110))
                    else:
                        if b <= len(table) and (table[i] != 0) and (ctime % flash_time) <= flash_time/2: qp.setBrush(current_colour)
                    r1 = QRectF(12, y-5, width-24, radius + 9)
                    qp.drawRoundedRect(r1, 6, 6)
                    
                    pen = QPen(foreground_colour)
                    pen.setStyle(Qt.PenStyle.SolidLine)
                    qp.setPen(pen)

                    if table[i] != 0: 
                        qp.setBrush(current_colour)
                        qp.setPen(QColor('#FFFFFF'))
                    else: 
                        qp.setBrush(Qt.BrushStyle.NoBrush)
                        qp.setPen(foreground_colour)

                    qp.drawEllipse(QRectF(x, y-1, radius, radius))

                    text = i
                    text_x = x + radius + 6
                    text_y = y+12
                    font = QFont()
                    font.setPointSizeF(13)
                    qp.setFont(font)
                    if table[i] != 0 and (ctime % flash_time) <= flash_time/2: qp.setPen(QColor('#FFFFFF'))
                    else: qp.setPen(foreground_colour)
                    font_metrics = QFontMetrics(font)
                    text_width = font_metrics.horizontalAdvance(text)
                    if text_width > total_width: total_width = text_width

                    if text_width > width-45:
                        truncated_text = font_metrics.elidedText(text, Qt.TextElideMode.ElideRight, width-45)
                        qp.drawText(QPointF(text_x, text_y), truncated_text)
                    else:
                        qp.drawText(text_x, text_y, text)
                    
                    b += 1

            self.setMinimumHeight(b*27 + 8)
        else:
            qp.setPen(foreground_colour)
            font = QFont()
            font.setPointSizeF(16)
            qp.setFont(font)
            text = "NetworkTable not connected"
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(text)/2
            text_height = font_metrics.height()
            qp.drawText(QPointF(width/2-text_width, height/2+text_height/4), text)
            self.setMinimumHeight(text_height)