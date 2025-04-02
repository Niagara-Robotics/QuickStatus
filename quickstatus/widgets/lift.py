from quickstatus.utils.imports import *
from quickstatus.utils.generic import *
from quickstatus.utils.network_tables import datatable, NetworkTables
import random

test = 1

class LiftWidget(QWidget):
    name = 'Lift'
    def __init__(self, wid, conf):
        super(LiftWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        self.base_width = 1000
        self.base_height = 1500

        restoreWindow(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)

        self.old_dt = int(monotonic()*150)
        self.wr = 0
        self.rot_right = True
        self.aspect_ratio = 0.5

        self.load_gripper()

        self.global_font = global_config.data['general']['global_font']

    def load_gripper(self):
        with open('resources/widgets/lift/gripper.coords') as gripper_file:
            self.gripper_rot_points = []
            for line in gripper_file:
                coords = line.strip().split(", ")
                if len(coords) == 2:
                    self.gripper_rot_points.append(QPointF(float(coords[0]), float(coords[1])))
    
    def resizeEvent(self, event):
        resize_window(self)
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        # setup canvas & variables
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        
        cw, ch = self.width_cache/2, self.height_cache/2 # centre width, centre height
        dt = int(monotonic() * 150)

        # ensure NetworkTable data exists
        table = datatable[self.config['network-table']]
        dash = datatable[self.config['gripper-table']]

        scale = self.scale

        if NetworkTables.inst.isConnected():
            qp.scale(scale,scale)
            qp.translate(cw/scale-250,ch/scale+130)

            self.check_data(table, dash)

            if self.lift_height is not None or self.gripper_rot is not None:
                self.draw_lift(qp)
            
            subwidget_pos = (475, 50)
            if global_config.data['general']['show-unused-widgets']: self.draw_arm_rotation(qp, subwidget_pos)
            else: qp.translate(0, -100)
            if self.gripper_distance is not None: self.draw_sensor_values(qp, subwidget_pos)
            self.draw_gripper_subwidget(qp, 50, subwidget_pos, dt)
            qp.translate(0, -300)
            if self.calibration_state is not None: self.draw_calibration(qp, (subwidget_pos[0], subwidget_pos[1]+525))
            
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
    
    def check_data(self, table, dash):
        try: self.gripper_rot = table['encoder_position']*360
        except: self.gripper_rot = None

        try: self.lift_height = table['position']/4.2
        except: self.lift_height = None

        try: self.calibration_state = table['calibration_state']
        except: self.calibration_state = None

        try: self.gripper_distance = dash['gripper_distance']
        except: self.gripper_distance = None

        try: self.gripper_coral = dash['gripper_coral']
        except: self.gripper_coral = None

        try: self.gripper_ambient = dash['gripper_ambient']
        except: self.gripper_ambient = None
    
    def draw_lift(self, qp:QPainter):
        qp.setPen(QPen(self.foreground_colour, 8, join=Qt.PenJoinStyle.RoundJoin))
        qp.setBrush(Qt.BrushStyle.NoBrush)
        qp.drawRoundedRect(QRectF(-125,-25,250,550), 0,0)
        if self.lift_height is not None:
            qp.drawRoundedRect(QRectF(-100,-self.lift_height*500,200,500), 0,0)

        # arm
        if self.gripper_rot is not None and global_config.data['general']['show-unused-widgets']:
            self.draw_lift_arm(qp, QPolygonF(self.gripper_rot_points))

        # arm line
        if self.lift_height is not None:
            self.draw_lift_line(qp)
    
    def draw_lift_arm(self, qp:QPainter, polygon):
        qp.save()
        height = self.lift_height if self.lift_height is not None else 0.5
        qp.translate(0,-height*1000+500)
        qp.rotate(self.gripper_rot*50)
        # draw arm outline
        qp.setPen(QPen(self.background_colour, 24))
        qp.drawPolygon(polygon)

        qp.setBrush(self.foreground_colour)
        qp.setPen(QPen(self.foreground_colour, 4, join=Qt.PenJoinStyle.RoundJoin))
        qp.drawPolygon(polygon)
        qp.setBrush(self.background_colour)
        qp.setPen(QPen(self.foreground_colour, 8, join=Qt.PenJoinStyle.RoundJoin))
        qp.drawEllipse(QPoint(0,0),25,25)

        qp.restore()
   
    def draw_lift_line(self, qp:QPainter):
        qp.setPen(QPen(self.background_colour, 24))
        height = self.lift_height if self.lift_height is not None else 0.5
        al_trans = -height*1000+500
        qp.drawLine(QLineF(-100,al_trans,100,al_trans))
        qp.setPen(QPen(self.foreground_colour, 8))
        qp.drawLine(QLineF(-100,al_trans,100,al_trans))
    
    def draw_arm_rotation(self, qp:QPainter, pos:tuple):
        qp.setPen(QPen(self.foreground_colour, 8, join=Qt.PenJoinStyle.RoundJoin))
        qp.save()
        arr_size = 60
        grip_size = 125
        arrow_width = 50
        arr_color = self.palette().color(self.palette().ColorRole.Text)
        qp.translate(pos[0], pos[1]+grip_size*2+25)
        qp.drawEllipse(QPoint(0,0),grip_size,grip_size)
        qp.setPen(QPen(self.foreground_colour, 4))

        for i in range(4):
            lw = 1.5-(i%2 * 0.25)
            qp.drawLines([
            QPointF(0,-grip_size),QPointF(0,-grip_size/lw),
            QPointF(0,grip_size),QPointF(0,grip_size/lw),
            QPointF(-grip_size,0),QPointF(-grip_size/lw,0),
            QPointF(grip_size,0),QPointF(grip_size/lw,0),])
            arr_color.setAlpha(int(255/(i%2+1)))
            qp.setPen(QPen(arr_color, 4))
            qp.rotate(22.5)
        
        qp.setPen(QPen(self.foreground_colour, 4))
        qp.rotate(12-90)
        qp.setBrush(self.foreground_colour)
        qp.drawPolygon([QPointF(-arrow_width,-arr_size/2),QPointF(-arrow_width,arr_size/2),QPointF(-arr_size/1.5-arrow_width,0)])
        qp.drawPolygon([QPointF(arrow_width,-arr_size/2),QPointF(arrow_width,arr_size/2),QPointF(arr_size/1.5+arrow_width,0)])
        qp.setPen(QPen(self.foreground_colour, 12))
        qp.drawLine(QPointF(-arrow_width, 0), QPointF(arrow_width, 0))
        qp.restore()
    
    def draw_sensor_values(self, qp:QPainter, wheel_pos:tuple):
        lift_sensor = int(self.gripper_distance)
        ambient = self.gripper_ambient if self.gripper_ambient is not None else 0
        if ambient > 200:
            badness_level = 4
            text = "nil"
        else:
            badness_level = 1
            text = str(lift_sensor)+"mm"

        self.font = QFont(self.global_font)
        self.font.setPixelSize(80)
        self.font_met = QFontMetrics(self.font)
        ls_width = self.font_met.horizontalAdvance(text)
        ls_height = self.font_met.height()
        
        qp.setFont(self.font)
        qp.drawText(QPointF(wheel_pos[0]-ls_width/2,wheel_pos[1]+60),text)
        qp.setPen(QPen(self.colour_chart[badness_level], 8, Qt.PenStyle.DashLine, join=Qt.PenJoinStyle.RoundJoin))
        qp.drawRect(QRectF(wheel_pos[0]-ls_width/2-25,wheel_pos[1]-25,ls_width+50,ls_height+25))
    
    def draw_gripper_subwidget(self, qp:QPainter, wheel_size:int, wheel_pos:tuple, dt:float):
        # self.rot_right = datatable...
        if (random.randrange(1,50) == 1): self.rot_right = not self.rot_right
        rot = self.rot_right.conjugate()*2-1

        translate = QPoint(wheel_pos[0]-wheel_size*2, wheel_pos[1]-475)
        qp.translate(translate)
        if self.gripper_coral:
            self.draw_gripper_coral(qp, wheel_size)  
        self.draw_gripper_shape(qp, wheel_size)
        self.draw_gripper_wheels(qp, 50, dt, rot)
        qp.translate(-translate)
    
    def draw_calibration(self, qp:QPainter, cal_pos:tuple):
        qp.setPen(QPen(self.foreground_colour, 8))
        qp.setBrush(Qt.BrushStyle.NoBrush)
        
        cal_state = self.calibration_state
        cal_text = "Calibration"
        cal_dist = 110
        max_width = 500
        self.font = QFont(self.global_font)
        self.font.setPixelSize(80)
        qp.setFont(self.font)
        self.font_met = QFontMetrics(self.font)
        qp.save()
        cal_width = self.font_met.horizontalAdvance(cal_text)
        cal_width_2 = int(cal_width/2)
        cal_height = self.font_met.height()
        if cal_width >= max_width: 
            scale = 1/(cal_width/max_width)
            qp.scale(scale, 1)
        else: scale = 1

        # draw text
        qp.drawText(QPointF((cal_pos[0]/scale-cal_width_2), cal_pos[1]), cal_text)
        qp.restore()
        qp.save()

        # draw icon
        qp.translate(cal_pos[0], cal_pos[1]-cal_height/4+cal_dist)
        if cal_state != 0: qp.rotate(45)
        xs = 30
        cs = 25
        if cal_state == 0 or cal_state == 3:
            if cal_state == 3:
                qp.drawLines([
                    QPoint(-xs, 0),
                    QPoint(xs, 0),
                    QPoint(0, -xs),
                    QPoint(0, xs)])
            else:
                qp.drawPoints([QPoint(-xs, 0), QPoint(0, 0), QPoint(xs, 0)])

            qp.setPen(QPen(Colours.death_colour, 6))
        elif cal_state == 1:
            qp.setPen(QPen(Colours.caution_colour, 8))
            qp.drawArc(QRectF(-40,-40, 80, 80 ), int(monotonic()*-4800), 960)
        elif cal_state == 2:
            pos = (10,20)
            qp.drawPolyline([
                QPoint(pos[0]-cs, pos[1]),
                QPoint(pos[0],pos[1]),
                QPoint(pos[0],pos[1]-cs*2)])
            qp.setPen(QPen(Colours.accent_colour, 6))
            
        if cal_state != 1: qp.drawEllipse(QPoint(0,0),50,50)
        qp.restore()
    
    def draw_gripper_shape(self, qp:QPainter, wheel_size:int):
        qp.setPen(QPen(self.foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap))
        bend_size = 50
        line_width = 50
        line_height = 100
        line_pos = 200
        qp.translate(wheel_size*2, 0)
        qp.drawLine(QPoint(-line_width,line_pos), QPoint(line_width,line_pos))
        qp.drawLine(QPoint(-line_width-bend_size,line_pos-bend_size), QPoint(-line_width-bend_size,line_pos-bend_size-line_height))
        qp.drawLine(QPoint(line_width+bend_size,line_pos-bend_size), QPoint(line_width+bend_size,line_pos-bend_size-line_height))
        qp.drawArc(QRect(QPoint(-line_width-bend_size, line_pos-bend_size*2-1),QPoint(-line_width+bend_size, line_pos-1)), 2880, 1440)
        qp.drawArc(QRect(QPoint(line_width-bend_size-1, line_pos-bend_size*2-1),QPoint(line_width+bend_size-1, line_pos-1)), -1440, 1440)
        qp.drawArc(QRectF(-wheel_size-15,-wheel_size+20,wheel_size*2+30,wheel_size*2+30),2880,2880)

        qp.drawLine(QPointF(-line_width/2,line_pos), QPointF(-line_width/2,line_pos+line_height*2))
        qp.drawLine(QPointF(line_width/2,line_pos), QPointF(line_width/2,line_pos+line_height*2))
        qp.translate(-wheel_size*2, 0)
    
    def draw_gripper_coral(self, qp:QPainter, wheel_size:int):
        qp.setPen(QPen(self.foreground_colour, 20))
        dist = self.gripper_distance if self.gripper_distance is not None else 0 
        qp.drawEllipse(QPointF(wheel_size*2,35-dist),30,30)
    
    def draw_gripper_wheels(self, qp: QPainter, wheel_size: int, dt: float, rot: float):
        # setup variables
        time_dif = (dt - self.old_dt) * 32 * rot
        self.wr += time_dif
        angle = -self.wr
        angle2 = self.wr + 1920
        self.old_dt = dt
        arc_size = 1.5 * wheel_size

        # draw wheels
        self.draw_gripper_wheel(qp, QPointF(0, 0), arc_size, wheel_size, rot, angle)
        self.draw_gripper_wheel(qp, QPointF(wheel_size*4, 0), arc_size, wheel_size, rot, angle2)
    
    def draw_gripper_wheel(self, qp: QPainter, position: QPointF, arc_size: float, wheel_size: int, rot: float, angle: float):
        qp.setPen(QPen(self.foreground_colour, 8))
        qp.setBrush(Qt.BrushStyle.NoBrush)
        # draw circle
        qp.translate(position)
        qp.drawEllipse(QPoint(0, 0), wheel_size, wheel_size)

        if global_config.data['general']['show-unused-widgets']:
            # draw velocity outline
            qp.setPen(QPen(self.background_colour, 24))
            qp.drawArc(QRectF(-arc_size, -arc_size, arc_size*2, arc_size*2), angle, 960)

            # draw velocity
            qp.setPen(QPen(Colours.velocity_colour, 8))
            qp.drawArc(QRectF(-arc_size, -arc_size, arc_size*2, arc_size*2), angle, 960)

            # draw arrow
            qp.setPen(Qt.PenStyle.NoPen)
            qp.setBrush(self.foreground_colour)
            tri_size = 20
            qp.drawPolygon([QPointF(-tri_size, tri_size * -rot), QPointF(tri_size, tri_size * -rot), QPointF(0, -tri_size * -rot)])

        qp.translate(-position)