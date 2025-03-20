from quickstatus.utils.imports import *
from quickstatus.utils.generic import *
from quickstatus.utils.network_tables import NetworkTables, datatable
from math import degrees

class IntakeWidget(QWidget):
    def __init__(self, wid, conf):
        super(IntakeWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        self.setWindowTitle('QuickStatus (Intake)')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.arrow_angle = 0
        self.rott = 0
        self.old_dt = int(monotonic()*150)
        self.nt_connected = False
    
    def resizeEvent(self, event):
        self.width_cache = self.width()
        self.height_cache = self.height()
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        
        cw, ch = self.width_cache/2, self.height_cache/2 # centre width, centre height
        dt = int(monotonic() * 150)
        
        table = datatable['intake']
        table_req = ['ambient', 'encoder_position', 'distance', 'present', 'voltage_out']
        if self.nt_connected == False:
            self.nt_connected = all(k in table for k in table_req)

        if NetworkTables.inst.isConnected() and self.nt_connected:
            scale = cw/500
            qp.scale(scale, scale)
            qp.translate(cw/scale,ch/scale)

            self.draw_intake(qp)

            font = QFont(global_font)

            self.draw_state(qp, font)
            self.draw_bay(qp, (125, -125), table, font)
        
        else: noNetworkTable(self)
    
    def setup_palette(self):
        global foreground_colour, background_colour
        palette = self.palette()
        foreground_colour = palette.color(palette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        if sys.platform == 'darwin': palette.setColor(QPalette.ColorRole.Window, dark)
        self.setPalette(palette)
        background_colour = palette.color(palette.ColorRole.Window)
        self.colour_chart = [foreground_colour, colours.accent_colour, colours.caution_colour, colours.warning_colour, colours.death_colour]
    
    def draw_intake(self, qp:QPainter, dt:float, table:dict):
        # setup variables
        qp.setPen(QPen(foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin))
        qp.setBrush(Qt.BrushStyle.NoBrush)

        arc_pos = (-300,-225)
        arc_size = 400
        arc_dist = 50
        arc_angle = 90*16
        arc_cen = (arc_pos[0]+arc_size/2,arc_pos[1]+arc_size/2)
        arc_rot = table['encoder_position']*-360
        
        time_dif = (dt-self.old_dt)
        self.arrow_angle += time_dif/2
        self.old_dt = dt
        arrow_angle = int(self.arrow_angle % 90)

        # draw
        qp.translate(arc_cen[0], arc_cen[1]+125)

        self.draw_bumper(qp)
        
        qp.translate(0, -arc_dist/2-arc_size/2)
        qp.rotate(arc_rot)

        self.draw_intake_frame(qp, arc_size, arc_dist, arc_angle)

        wheel_num = 4
        wheel_size = 1.3
        qp.translate(0, -(-arc_dist/2-arc_size/2))
        
        self.draw_intake_wheels(qp, wheel_num, arc_size, arc_size, arc_dist, wheel_size)
        self.draw_wheel_velocity(qp, table['voltage_out'], arrow_angle, arc_size, arc_dist, arc_angle)
        
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
        qp.setBrush(background_colour)
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
            qp.setBrush(colours.velocity_colour)
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
            qp.setPen(QPen(colours.velocity_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin))
            if arrow_up: qp.drawArc(QRectF(-arc_size/2-arc_dist*2, -arc_dist*1.5, arc_size+arc_dist*4, arc_size+arc_dist*4), -arc_angle*2, -arrow_angle*16)
            else: qp.drawArc(QRectF(-arc_size/2-arc_dist*2, -arc_dist*1.5, arc_size+arc_dist*4, arc_size+arc_dist*4), arc_angle*2-1440, arrow_angle*16)
            qp.setPen(QPen(foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin))
    
    def draw_state(self, qp:QPainter, font:QFont):
        font.setPixelSize(80)
        qp.setFont(font)
        qp.translate(0,-200)

        qp.setPen(QPen(foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin))
        qp.setBrush(Qt.BrushStyle.NoBrush)

        qp.drawRect(QRectF(-415,285,580,130))

        action_text = "Algae Pickup"
        state_text = "Coral VA"

        qp.drawText(-380,377, action_text)
        font.setPixelSize(70)
        qp.setFont(font)
        qp.setF
        qp.drawText(-380,500, state_text)
        qp.translate(0,200)
    
    def draw_bay(self, qp:QPainter, pos:tuple, table:dict, font:QFont):
        font.setPixelSize(70)
        qp.setFont(font)
        qp.translate(pos[0],pos[1])
        bay_num = round(table['distance'])
        bay_amb = round(table['ambient'])
        if bay_amb > 32:
            badness_level = 4
            text = "nil"
        else:
            badness_level = 1
            text = str(bay_num)+"mm"

        qp.drawPolyline([QPointF(-100,0), QPointF(-50,125), QPointF(50,125), QPointF(100,0)])
        qp.setPen(QPen(self.colour_chart[badness_level], 8, Qt.PenStyle.DotLine))
        qp.drawLine(QLineF(-75,100,75,100))
        
        qp.setPen(QPen(foreground_colour, 25))
        if table['present']: qp.drawEllipse(QPointF(0,25),50,50)

        qp.drawText(125,75, text)
        qp.translate(-pos[0],-pos[1])