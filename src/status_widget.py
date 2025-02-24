from common import *
from time import time

things = ["Not working", "Working fine", "Proceed with caution", "Warning: maybe bad", "Deep trouble"]
values = [0,1,2,3,4]
for i in range(5): 
    things.append("Test")
    values.append(0)

refresh = 10
start_time = time()

class StatusWidget(QWidget):
        
    def __init__(self, conf):
        super(StatusWidget, self).__init__()
        self.num_circles = len(things)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(refresh)
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
        #accent_colour = palette.color(QPalette.ColorRole.Accent).lighter(115)
        background_colour = QPalette().color(QPalette().ColorRole.Window)
        foreground_colour = palette.color(palette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        palette.setColor(QPalette.ColorRole.Window, dark)
        self.setPalette(palette)
        flash_time = 100
        qp.setPen(foreground_colour)
        size = self.size()
        width = size.width()
        height = size.height()
        #qp.fillRect(self.rect(), QColor(background_colour))
        total_width = 0
        blink_speed = self.config['blink-interval']
        ctime = (time() - start_time) # how long the program has been running

        for i in range(self.num_circles):
            x = 12
            y = (i * 27) + 10
            radius = 16

            pen = QPen(Qt.PenStyle.NoPen)

            flash_time = ctime
            if values[i] == 1: 
                current_colour = accent_colour
            if values[i] == 2: 
                current_colour = caution_colour
            if values[i] == 3: 
                current_colour = warning_colour
            if values[i] == 4: 
                current_colour = death_colour
                if blink_speed > 0: flash_time = blink_speed*2
            
            pen.setStyle(Qt.PenStyle.NoPen)
            qp.setPen(pen)
            if i % 2 == 0: 
                qp.setBrush(Qt.BrushStyle.NoBrush)
                if (values[i] != 0) and (ctime % flash_time) <= flash_time/2: qp.setBrush(current_colour.darker(110))
            else:
                qp.setBrush(background_colour)
                if (values[i] != 0) and (ctime % flash_time) <= flash_time/2: qp.setBrush(current_colour)
            r1 = QRectF(4, y-5, width-8, radius + 9)
            qp.drawRoundedRect(r1, 6, 6)
            
            pen = QPen(foreground_colour)
            pen.setStyle(Qt.PenStyle.SolidLine)
            qp.setPen(pen)
            if values[i] != 0: qp.setBrush(current_colour)
            else: qp.setBrush(Qt.BrushStyle.NoBrush)
            if values[i] == 0: qp.setPen(foreground_colour)
            else: qp.setPen(QColor('#FFFFFF'))
            qp.drawEllipse(QRectF(x, y-1, radius, radius))

            text = things[i]
            text_x = x + radius + 6
            text_y = y+12
            font = QFont()
            font.setPointSizeF(13)
            qp.setFont(font)
            if values[i] != 0 and (ctime % flash_time) <= flash_time/2: qp.setPen(QColor('#FFFFFF'))
            else: qp.setPen(foreground_colour)
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(text)
            if text_width > total_width: total_width = text_width

            if text_width > width-45:
                truncated_text = font_metrics.elidedText(text, Qt.TextElideMode.ElideRight, width-45)
                qp.drawText(QPointF(text_x, text_y), truncated_text)
            else:
                qp.drawText(text_x, text_y, text)

        self.setMinimumHeight(len(things)*27 + 8)