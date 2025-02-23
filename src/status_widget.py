from common import *
from time import time

things = ["Not working", "Working fine", "Proceed with caution", "Warning: maybe bad", "Deep trouble"]
values = [0, 1, 2, 3, 4]

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
        if self.config['scroll-horizontal'] == False: minX = 0
        else: minX = 100000
        if self.config['scroll-vertical'] == False: minY = 0
        else: minY = 100000

        return QSize(minX, minY)
        
    # draw status lights
    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        palette = self.palette()
        #accent_colour = palette.color(QPalette.ColorRole.Accent).lighter(115)
        background_colour = palette.color(QPalette.ColorRole.Window)
        foreground_colour = palette.color(QPalette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        dark = palette.color(QPalette.ColorRole.Mid)
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
            x = 4
            y = (i * 20) + 4
            radius = 13

            pen = QPen(dark)
            qp.setPen(pen)

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
            

            if i % 2 == 0: 
                qp.setBrush(dark)
                if (values[i] != 0) and (ctime % flash_time) <= flash_time/2: qp.setBrush(current_colour.darker(130))
            else:
                qp.setBrush(background_colour)
                if (values[i] != 0) and (ctime % flash_time) <= flash_time/2: qp.setBrush(current_colour)
            r1 = QRect(0, y-3, width, radius + 6)
            qp.drawRect(r1)
            
            pen = QPen(foreground_colour)
            pen.setStyle(Qt.PenStyle.SolidLine)
            qp.setPen(pen)
            if values[i] != 0: qp.setBrush(current_colour)
            else: qp.setBrush(background_colour)
            qp.drawEllipse(x, y, radius, radius)

            text = things[i]
            text_x = x + radius + 5
            text_y = int(y+11)
            font = QFont()
            if sys.platform == 'darwin': font.setPointSizeF(12)
            else: font.setPointSizeF(11)
            qp.setFont(font)
            qp.setPen(foreground_colour)
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(text)
            if text_width > total_width: total_width = text_width

            if text_width > width-20:
                truncated_text = font_metrics.elidedText(text, Qt.TextElideMode.ElideRight, width-20)
                qp.drawText(text_x, text_y, truncated_text)
            else:
                qp.drawText(text_x, text_y, text)
        self.setMaximumWidth(total_width+30)
        self.setMaximumHeight(len(things)*20)