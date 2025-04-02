from quickstatus.utils.generic import *
from quickstatus.utils.network_tables import NetworkTables, datatable
from moms_apriltag import TagGenerator2

class VisionWidget(QWidget):
    name = 'Vision'
    def __init__(self, wid, conf):
        super(VisionWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        self.base_width = 1000
        self.base_height = 1000

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)

        self.global_font = global_config.data['general']['global_font']

        self.vision_states = [
            'Standby',
            'Evil Scary Vision Mode'
        ]
        self.latency = 0

        self.setup_bar(width=600, height=20, ticks=3)
        self.tag_cache = {}
        self.setup_tags(min_id=1, max_id=22)
    
    def setup_bar(self, width:int, height:int, ticks:int):
        self.bar_width = width
        self.bar_height = height
        self.tick_pos = []

        for i in range(ticks):
            x = self.bar_width*((i+1)/(ticks+1)) - self.bar_width/2
            self.tick_pos.append(QLineF(x,-self.bar_height-10, x,10))
    
    def setup_tags(self, min_id:int, max_id:int):
        tg = TagGenerator2("tag36h11")
        for tag_id in range(min_id, max_id+1):
            tag = tg.generate(tag_id)
            height, width = tag.shape
            self.tag_cache[tag_id] = QImage(tag.data, width, height, QImage.Format.Format_Grayscale8)
    
    def resizeEvent(self, event):
        resize_window(self)
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        
        cw, ch = self.width_cache/2, self.height_cache/2 # centre width, centre height
        
        #table = datatable[self.config['network-table']]

        if NetworkTables.inst.isConnected() or True:
            scale = self.scale
            qp.scale(scale, scale)
            qp.translate(cw/scale,ch/scale)

            #self.check_data(table)

            font = QFont(self.global_font)
            self.state = self.vision_states[0]
            self.current_tag = 1
            if not self.current_tag in self.tag_cache:
                self.setup_tags(self.current_tag, self.current_tag)

            self.draw_state(qp, font, (-400,150))
            if self.latency is not None: self.draw_latency_bar(qp, font, (0,400))

            if self.current_tag is not None: self.draw_tag(qp, font, (100,-200), 400)

        else: noNetworkTable(self)
    
    def setup_palette(self):
        palette = self.palette()

        self.background_colour = palette.color(palette.ColorRole.Window)

        self.foreground_colour = palette.color(palette.ColorRole.Text)
        self.foreground_colour.setAlpha(255)

        dark = palette.color(palette.ColorRole.Base).lighter(160)
        palette.setColor(QPalette.ColorRole.Window, dark)
        
        self.setPalette(palette)
        self.colour_chart = [self.foreground_colour, Colours.accent_colour, Colours.caution_colour, Colours.warning_colour, Colours.death_colour]
    
    def check_data(self, table):
        try: self.ambient = table['ambient']
        except: self.ambient = None

        try: self.encoder_position = table['encoder_position']
        except: self.encoder_position = None

        try: self.distance = table['distance']
        except: self.distance = None

        try: self.present = table['present']
        except: self.present = None

        try: self.voltage_out = table['voltage_out']
        except: self.voltage_out = None

        try: self.state = self.intake_states[int(table['state'])]
        except: self.state = None

        try: self.action = self.intake_actions[int(table['action'])]
        except: self.action = None
    
    def draw_state(self, qp:QPainter, font:QFont, pos:tuple):
        # setup variables
        font.setPixelSize(80)
        qp.setFont(font)

        qp.setPen(QPen(self.foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin))
        qp.setBrush(Qt.BrushStyle.NoBrush)

        state_text = self.state

        # draw state
        rect = QRect(pos[0],pos[1],580,130)
        qp.drawRect(rect)

        if self.state is not None:
            qp.drawText(rect.adjusted(40,0,0,0), Qt.AlignmentFlag.AlignVCenter, state_text)

    def draw_latency_bar(self, qp:QPainter, font:QFont, pos:tuple):
        # setup variables
        qp.translate(pos[0], pos[1])
        latency_max = 40
        width = self.bar_width
        width2 = int(self.bar_width/2)
        height = self.bar_height
        self.latency += 0.1
        self.latency %= 60

        # bar outline
        qp.setPen(QPen(self.foreground_colour, 6, join=Qt.PenJoinStyle.MiterJoin))
        qp.drawRect(-width2, -height, width, height)

        # bar background
        qp.setPen(Qt.PenStyle.NoPen)
        qp.setBrush(self.background_colour.darker(100))
        qp.drawRect(-width2, -height, width, height)
        if self.latency <= latency_max:
            if self.latency >= 20: 
                if self.latency >= 30: qp.setBrush(Colours.warning_colour)
                else: qp.setBrush(Colours.caution_colour)
            else: qp.setBrush(Colours.accent_colour)
            latency_percent = self.latency/latency_max
        else:
            qp.setBrush(Colours.death_colour)
            latency_percent = 1

        # bar fill
        latency_width = int(width*latency_percent)
        qp.drawRect(-width2, -height, latency_width, height)

        # tick marks
        qp.setPen(QPen(self.foreground_colour, 4, cap=Qt.PenCapStyle.FlatCap))
        qp.drawLines(self.tick_pos)

        # text
        font.setPixelSize(40)
        qp.setFont(font)
        qp.drawText(width2+25,0, f'{latency_max}ms')

        latency_text = f'{int(self.latency)}ms'
        text_w = QFontMetrics(font).horizontalAdvance(latency_text)
        qp.drawText(-width2-25-text_w,0, latency_text)
        
        qp.translate(-pos[0], -pos[1])
    
    def draw_tag(self, qp:QPainter, font:QFont, pos:tuple, size:int):
        # setup variables
        font.setPixelSize(60)
        qp.setFont(font)
        qp.setPen(QPen(self.foreground_colour, 12, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.MiterJoin))
        qp.setBrush(self.background_colour.darker(100))
        
        # draw apriltag
        size2 = int(size/2)
        rect = QRect(pos[0]-size2, pos[1]-size2, size, size)
        qp.drawRect(rect)

        qp.setPen(Qt.PenStyle.NoPen)
        qp.drawRect(rect)

        qp.setPen(QPen(self.foreground_colour, 12, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.MiterJoin))
        qp.drawText(rect, Qt.AlignmentFlag.AlignCenter, 'No\nAprilTag')

        if True:
            qp.drawImage(rect, self.tag_cache[self.current_tag])
            text = f'ID {self.current_tag}'
        else: text = 'nil'

        # draw ID
        font.setPixelSize(100)
        qp.setFont(font)
        qp.drawText(rect.adjusted(-size,0,-size,0), Qt.AlignmentFlag.AlignCenter, text)
        