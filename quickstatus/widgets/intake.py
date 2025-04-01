from quickstatus.utils.generic import *
from quickstatus.utils.network_tables import NetworkTables, datatable

class IntakeWidget(QWidget):
    name = 'Intake'
    def __init__(self, wid, conf):
        super(IntakeWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        self.base_width = 1000
        self.base_height = 1000

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.arrow_angle = 0
        self.rott = 0
        self.old_dt = int(monotonic()*150)

        self.global_font = global_config.data['general']['global_font']

        self.intake_states = [
            'Standby',
            'Algae Pickup',
            'Algae Locked',
            'Coral VA',
            'Coral Horizontal',
            'Coral VB'
        ]
        self.intake_actions = [
            'Standby',
            'Pickup Coral',
            'Pickup Algae',
            'Eject Algae'
        ]
    
    def resizeEvent(self, event):
        resize_window(self)
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        
        cw, ch = self.width_cache/2, self.height_cache/2 # centre width, centre height
        dt = int(monotonic() * 150)
        
        table = datatable[self.config['network-table']]

        if NetworkTables.inst.isConnected():
            scale = self.scale
            qp.scale(scale, scale)
            qp.translate(cw/scale,ch/scale)

            self.check_data(table)

            if self.encoder_position is not None or self.voltage_out is not None:
                self.draw_intake(qp, dt)

            font = QFont(self.global_font)

            if self.state is not None or self.action is not None: self.draw_state(qp, font)
            if self.distance is not None: self.draw_bay(qp, (125, -125), font)
        
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
    
    def draw_intake(self, qp:QPainter, dt:float):
        # setup variables
        qp.setPen(QPen(self.foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin))
        qp.setBrush(Qt.BrushStyle.NoBrush)

        arc_pos = (-300,-225)
        arc_size = 400
        arc_dist = 50
        arc_angle = 90*16
        arc_cen = (arc_pos[0]+arc_size/2,arc_pos[1]+arc_size/2)
        arc_rot = self.encoder_position*-360 if self.encoder_position is not None else 0
        
        time_dif = (dt-self.old_dt)
        self.arrow_angle += time_dif/2
        self.old_dt = dt
        arrow_angle = int(self.arrow_angle % 90)

        # draw
        qp.translate(arc_cen[0], arc_cen[1]+125)

        self.draw_bumper(qp, arc_size, arc_dist)
        
        qp.translate(0, -arc_dist/2-arc_size/2)
        qp.rotate(arc_rot)
        if self.encoder_position is not None: self.draw_intake_frame(qp, arc_size, arc_dist, arc_angle)

        wheel_num = 4
        wheel_size = 1.3
        qp.translate(0, -(-arc_dist/2-arc_size/2))
        
        if self.encoder_position is not None: self.draw_intake_wheels(qp, wheel_num, arc_size, arc_dist, wheel_size)
        if self.voltage_out is not None: self.draw_wheel_velocity(qp, self.voltage_out, arrow_angle, arc_size, arc_dist, arc_angle)
        
        qp.rotate(-arc_rot)
        qp.translate(-arc_cen[0], -(arc_pos[1]-arc_dist/2))
    
    def draw_bumper(self, qp:QPainter, arc_size:int, arc_dist:int):
        bumper_size = arc_size/4
        qp.drawPolyline([QPointF(-bumper_size,arc_dist), QPointF(-bumper_size,-bumper_size),QPointF(arc_dist,-bumper_size)])
    
    def draw_intake_frame(self, qp:QPainter, arc_size:int, arc_dist:int, arc_angle:int):
        qp.drawArc(QRectF(-arc_size/2, arc_dist/2, arc_size, arc_size), arc_angle, arc_angle)
        qp.drawArc(QRectF(-arc_size/2-arc_dist, 0-arc_dist/2, arc_size+arc_dist*2, arc_size+arc_dist*2), arc_angle, arc_angle)

        qp.drawArc(QRectF(-arc_size/2-arc_dist, arc_size/2-1, arc_dist, arc_dist), arc_angle*2, arc_angle*2)
        qp.drawArc(QRectF(-arc_size/2+arc_size/2-arc_dist/2-1, -arc_dist/2, arc_dist, arc_dist), -arc_angle, arc_angle*2)

    def draw_intake_wheels(self, qp:QPainter, wheel_num:int, arc_size:int, arc_dist:int, wheel_size:int):
        qp.setBrush(self.background_colour)
        for i in range(wheel_num):
            rot = -90/wheel_num*(i+1)
            rot = rot+90/wheel_num/2
            qp.rotate(rot)
            qp.drawEllipse(QPointF(0,-arc_size/2-arc_dist/2), arc_dist/2*wheel_size, arc_dist/2*wheel_size)
            qp.rotate(-rot)
    
    def draw_wheel_velocity(self, qp:QPainter, arrow_current:float, arrow_angle:int, arc_size:int, arc_dist:int, arc_angle:int):
        if arrow_current != 0:
            if arrow_current > 0: arrow_up = True
            else: arrow_up = False
            qp.save()
            qp.setBrush(Colours.velocity_colour)
            qp.setPen(Qt.PenStyle.NoPen)
            tri_size = 35
            if arrow_up: qp.rotate(-90+arrow_angle)
            else: qp.rotate(-arrow_angle)
            qp.translate(0,-arc_size/2-arc_dist*2)
            if arrow_up: qp.drawPolygon([QPointF(-1,-tri_size/2),QPointF(-1,tri_size/2),QPointF(tri_size-1,0)])
            else: qp.drawPolygon([QPointF(-1,-tri_size/2),QPointF(-1,tri_size/2),QPointF(-tri_size-1,0)])
            
            qp.restore()
        qp.translate(0, -(arc_size/2+arc_dist/2))
        if arrow_current != 0:
            qp.setPen(QPen(Colours.velocity_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin))
            if arrow_up: qp.drawArc(QRectF(-arc_size/2-arc_dist*2, -arc_dist*1.5, arc_size+arc_dist*4, arc_size+arc_dist*4), -arc_angle*2, -arrow_angle*16)
            else: qp.drawArc(QRectF(-arc_size/2-arc_dist*2, -arc_dist*1.5, arc_size+arc_dist*4, arc_size+arc_dist*4), arc_angle*2-1440, arrow_angle*16)
            qp.setPen(QPen(self.foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin))
    
    def draw_state(self, qp:QPainter, font:QFont):
        font.setPixelSize(80)
        qp.setFont(font)
        qp.translate(0,-200)

        qp.setPen(QPen(self.foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin))
        qp.setBrush(Qt.BrushStyle.NoBrush)

        action_text = self.action
        state_text = self.state

        if self.action is not None:
            qp.drawRect(QRectF(-415,285,580,130))
            qp.drawText(-380,377, action_text)

        font.setPixelSize(70)
        qp.setFont(font)
        if self.state is not None:qp.drawText(-380,500, state_text)
        qp.translate(0,200)
    
    def draw_bay(self, qp:QPainter, pos:tuple, font:QFont):
        font.setPixelSize(70)
        qp.setFont(font)
        qp.translate(pos[0],pos[1])
        bay_num = round(self.distance)
        bay_amb = round(self.ambient) if self.ambient is not None else 0
        if bay_amb > 32:
            badness_level = 4
            text = "nil"
        else:
            badness_level = 1
            text = str(bay_num)+"mm"

        qp.drawPolyline([QPointF(-100,0), QPointF(-50,125), QPointF(50,125), QPointF(100,0)])
        qp.setPen(QPen(self.colour_chart[badness_level], 8, Qt.PenStyle.DotLine))
        qp.drawLine(QLineF(-75,100,75,100))
        
        qp.setPen(QPen(self.foreground_colour, 25))
        if self.present: qp.drawEllipse(QPointF(0,25),50,50)

        qp.drawText(125,75, text)
        qp.translate(-pos[0],-pos[1])