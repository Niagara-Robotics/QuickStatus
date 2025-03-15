from quickstatus.utils.imports import *
from quickstatus.utils.generic import *
from quickstatus.utils.network_tables import datatable, NetworkTables
import random

class LiftWidget(QWidget):
    def __init__(self, wid, conf):
        super(LiftWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        self.setWindowTitle('QuickStatus (Lift State)')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        lift = open('resources/widgets/lift/lift.coords')
        self.liftv = []
        liftl = []
        b = 0
        for i in lift:
            liftl.append(i.strip("\n"))
            self.liftv.append(QPointF(float(liftl[b].split(", ")[0]), float(liftl[b].split(", ")[1])))
            b += 1
        lift.close()
        self.old_dt = int(monotonic()*150)
        self.wr = 0
        self.rot_right = True

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        palette = self.palette()
        foreground_colour = palette.color(palette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        if sys.platform == 'darwin': palette.setColor(QPalette.ColorRole.Window, dark)
        background_colour = self.palette().color(self.palette().ColorRole.Window)
        self.setPalette(palette)
        colour_chart = [foreground_colour, colours.accent_colour, colours.caution_colour, colours.warning_colour, colours.death_colour]
        size = self.size()
        w = size.width()
        h = size.height()
        cw = w/2 # canvas width
        ch = h/2 # canvas height
        dt = int(monotonic()*150)

        table = datatable['lift']
        dash = datatable['SmartDashboard']
        if NetworkTables.inst.isConnected() and len(table) >= 4 and len(dash) >= 20:
            qp.setBrush(foreground_colour)
            qp.setPen(QPen(foreground_colour, 8, join=Qt.PenJoinStyle.RoundJoin))
            scale = cw/525
            qp.scale(scale,scale)
            qp.translate(cw/scale-250,ch/scale+50)
            qp.save()
            lift = QPolygonF(self.liftv)
        
            irx1 = 50
            iry1 = 300
            self.arm = table['encoder_position']*360
            self.elev1 = 0
            self.elev2 = table['position']/4.2
            self.elev3 = self.elev2

            # elevators
            qp.restore()
            qp.setBrush(Qt.BrushStyle.NoBrush)
            qp.save()
            qp.drawRoundedRect(QRectF(-125,-25-self.elev1*500,250,550), 0,0)
            qp.drawRoundedRect(QRectF(-100,-self.elev2*500,200,500), 0,0)

            # arm
            qp.translate(0,-self.elev2*500+500-self.elev3*500)
            qp.rotate(self.arm*50)
            qp.translate(-irx1,-iry1) # rotate from middle bottom
            qp.setPen(QPen(background_colour, 24))
            qp.drawPolygon(lift)
            qp.setBrush(foreground_colour)
            qp.setPen(QPen(foreground_colour, 4, join=Qt.PenJoinStyle.RoundJoin))
            qp.drawPolygon(lift)
            qp.setBrush(background_colour)
            qp.setPen(QPen(foreground_colour, 8, join=Qt.PenJoinStyle.RoundJoin))
            qp.drawEllipse(QPointF(irx1,iry1),25,25)

            qp.restore()
            qp.save()

            # arm line
            qp.setPen(QPen(background_colour, 24))
            al_trans = -self.elev2*500+500-self.elev3*500
            qp.drawLine(QLineF(-100,al_trans,100,al_trans))
            qp.setPen(QPen(foreground_colour, 8))
            qp.drawLine(QLineF(-100,al_trans,100,al_trans))

            # arm rotation
            wheel_size = 50
            wheel_pos = (500,0)

            arr_size = 60
            grip_size = 125
            arrow_width = 50
            arr_color = palette.color(palette.ColorRole.Text)
            qp.translate(wheel_pos[0], grip_size*2+25)
            qp.drawEllipse(QPoint(0,0),grip_size,grip_size)
            qp.setPen(QPen(foreground_colour, 4))

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
            
            qp.setPen(QPen(foreground_colour, 4))
            qp.rotate(12-90)
            qp.setBrush(foreground_colour)
            qp.drawPolygon([QPointF(-arrow_width,-arr_size/2),QPointF(-arrow_width,arr_size/2),QPointF(-arr_size/1.5-arrow_width,0)])
            qp.drawPolygon([QPointF(arrow_width,-arr_size/2),QPointF(arrow_width,arr_size/2),QPointF(arr_size/1.5+arrow_width,0)])
            qp.setPen(QPen(foreground_colour, 12))
            qp.drawLine(QPointF(-arrow_width, 0), QPointF(arrow_width, 0))
            qp.restore()

            lift_sensor = int(dash['gripper_distance'])
            ambient = dash['gripper_ambient']
            if ambient > 200:
                badness_level = 4
                text = "nil"
            else:
                badness_level = 1
                text = str(lift_sensor)+"mm"

            font = QFont('Iosevka Aile')
            font.setPixelSize(80)
            font_met = QFontMetrics(font)
            ls_width = font_met.horizontalAdvance(text)
            ls_height = font_met.height()
            qp.setFont(font)
            qp.drawText(QPointF(wheel_pos[0]-ls_width/2,wheel_pos[1]+60),text)
            qp.save()
            qp.setPen(QPen(colour_chart[badness_level], 8, Qt.PenStyle.DashLine, join=Qt.PenJoinStyle.RoundJoin))
            qp.drawRect(QRectF(wheel_pos[0]-ls_width/2-25,wheel_pos[1]-25,ls_width+50,ls_height+25))
            qp.restore()

            cal_state = table['calibration_state']
            cal_text = "Calibration"
            cal_pos = (150, 525)
            cal_dist = 50
            cal_width = font_met.horizontalAdvance(cal_text)
            cal_height = font_met.height()
            qp.drawText(cal_pos[0], cal_pos[1], cal_text)
            qp.setPen(QPen(foreground_colour, 8))
            qp.save()
            qp.translate(cal_pos[0]+cal_width+cal_dist+25, cal_pos[1]-cal_height/4)
            qp.rotate(45)
            xs = 30
            cs = 25
            if cal_state == 0:
                qp.drawLines([
                    QPoint(-xs,0),
                    QPoint(xs,0),
                    QPoint(0,-xs),
                    QPoint(0,xs)])
                qp.setPen(QPen(colours.death_colour, 4))
            elif cal_state == 1:
                qp.setPen(QPen(colours.caution_colour, 8))
                qp.drawArc(QRectF(-40,-40, 80, 80 ), int(monotonic()*-4800), 960)
            elif cal_state == 2:
                pos = (10,20)
                qp.drawPolyline([
                    QPoint(pos[0]-cs, pos[1]),
                    QPoint(pos[0],pos[1]),
                    QPoint(pos[0],pos[1]-cs*2)])
                qp.setPen(QPen(colours.accent_colour, 4))
                
            if cal_state != 1: qp.drawEllipse(QPoint(0,0),50,50)
            qp.restore()

            cr = self.rot_right
            # self.rot_right = datatable...
            if (random.randrange(1,50) == 1): self.rot_right = not self.rot_right
            rot = self.rot_right.conjugate()*2-1
            arc_size = 1.5 * wheel_size

            qp.translate(wheel_pos[0]-wheel_size*2, wheel_pos[1]-475)

            qp.setPen(QPen(foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap))
            qp.save()
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
            
            qp.setPen(QPen(foreground_colour, 25))
            dist = dash['gripper_distance']
            if dash['gripper_coral']: qp.drawEllipse(QPoint(0,35-dist),35,35)

            qp.restore()
            qp.save()
            qp.drawEllipse(QPointF(0,0),wheel_size,wheel_size)
            qp.setPen(QPen(background_colour, 24))
            time_dif = (dt-self.old_dt)*32*rot
            self.wr += time_dif
            angle = -self.wr
            angle2 = self.wr+1920
            self.old_dt = dt
            tri_size = 20
            qp.drawArc(QRectF(-arc_size, -arc_size, arc_size*2, arc_size*2), angle, 960)
            qp.setPen(QPen(colours.velocity_colour, 8))
            qp.drawArc(QRectF(-arc_size, -arc_size, arc_size*2, arc_size*2), angle, 960)
            qp.setPen(Qt.PenStyle.NoPen)
            qp.setBrush(foreground_colour)
            qp.drawPolygon([QPointF(-tri_size,tri_size*-rot),QPointF(tri_size,tri_size*-rot),QPointF(0,-tri_size*-rot)])

            qp.restore()
            qp.translate(wheel_size*4,0)
            qp.drawEllipse(QPoint(0,0),wheel_size,wheel_size)
            qp.setPen(QPen(background_colour, 24))
            qp.drawArc(QRectF(-arc_size, -arc_size, arc_size*2, arc_size*2), angle2, 960)
            qp.setPen(QPen(colours.velocity_colour, 8))
            qp.drawArc(QRectF(-arc_size, -arc_size, arc_size*2, arc_size*2), angle2, 960)
            qp.setPen(Qt.PenStyle.NoPen)
            qp.setBrush(foreground_colour)
            qp.drawPolygon([QPointF(-tri_size,tri_size*-rot),QPointF(tri_size,tri_size*-rot),QPointF(0,-tri_size*-rot)])
        
        else: noNetworkTable(self)