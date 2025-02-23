from common import *
from math import sqrt

class SwerveWidget(QWidget):
    def __init__(self, wid, conf):
        super(SwerveWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        self.setWindowTitle('QuickStatus (Swerve State)')
        self.resize(500,500)

        # Adjust the timer interval to match the monitor's refresh rate
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(refresh)
        self.base_rot = 45
        self.wheel_rot = [15,-5,86,-123]
        self.velocities = [0.59,-0.4,1,-0.1]
        self.targ_velocities = [0.7,-0.74,1,-0.7]
        self.powers = [0.76,-0.5,0.96,-0.6]
        self.wheel_status = [0,1,2,4]
        self.base_status = 3
    # draw status lights
    def paintEvent(self, event):
        #Setup
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        palette = self.palette()
        background_colour = palette.color(QPalette.ColorRole.Window)
        foreground_colour = palette.color(QPalette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        colour_chart = [foreground_colour, accent_colour, caution_colour, warning_colour, death_colour]
        size = self.size()
        w = size.width()
        h = size.height()
        cw = w/2 # canvas width
        ch = h/2 # canvas height
        rs = w*0.25 # box size
        cs = w*0.12 # circle radius

        # Rotate base
        qp.translate(cw,ch)
        qp.rotate(self.base_rot)

        #Base
        rx = rs*2
        ry = rs*0.6
        irx1 = rx*-0.5
        iry1 = ry*-(1/0.6)

        pen = QPen()
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setColor(colour_chart[self.base_status])
        pen.setWidthF(cw/60)
        qp.setPen(pen)
        qp.setBrush(colour_chart[self.base_status])
        qp.drawRect(QRectF(irx1, iry1, rx, ry))

        qp.setBrush(Qt.BrushStyle.NoBrush)
        qp.drawRect(QRectF(irx1, iry1, rx, rx))

        '''Draw Wheel'''
        for i in range(4):
            self.wheel_rot[i] -= 1
            if i%2: irx = -irx1
            else: irx = irx1
            if i>1: iry = -iry1
            else: iry = iry1
            qp.translate(irx,iry)
            if not self.config['wheel-lock']: qp.rotate(self.wheel_rot[i])
            else: qp.rotate(-self.br)
            #BG Circle
            pen.setStyle(Qt.PenStyle.NoPen)
            qp.setPen(pen)
            qp.setBrush(background_colour)

            qp.drawEllipse(QPointF(0,0),cs*1.1,cs*1.1)

            #Bar %s
            foreground_colour.setAlpha(150)
            qp.setPen(QPen(foreground_colour, cw/100))
            foreground_colour.setAlpha(255)
            qp.setBrush(Qt.BrushStyle.NoBrush)
            qp.drawLine(QLineF(-cs/2.4, 0, cs/2.4, 0))
            qp.drawLine(QLineF(-cs/2.4, -cs/2, cs/2.4, -cs/2))
            qp.drawLine(QLineF(-cs/2.4, cs/2, cs/2.4, cs/2))

            #Lines
            la=50 # line distance
            bd = cw/15
            bd2 = bd/2
            pen = QPen(foreground_colour, cw/90)
            qp.setPen(pen)
            qp.setBrush(Qt.BrushStyle.NoBrush)

            qp.drawChord(QRectF(-cs,-cs,cs*2,cs*2),(la*8)+(1440),((180-la)*16))
            qp.drawChord(QRectF(-cs,-cs,cs*2,cs*2),(-la*8)+(1440),(-(180-la)*16))
            
            qp.setPen(QPen(velocity_colour, bd, cap=Qt.PenCapStyle.FlatCap))
            qp.drawLine(QLineF(-bd2, 0, -bd2, -cs*self.velocities[i]))
            
            qp.setPen(QPen(power_colour, bd, cap=Qt.PenCapStyle.FlatCap))
            qp.drawLine(QLineF(bd2, 0, bd2, -cs*self.powers[i]))
            
            #Circle
            pen.setColor(colour_chart[self.wheel_status[i]])
            pen.setWidthF(cw/80)
            qp.setPen(pen)
            qp.setBrush(Qt.BrushStyle.NoBrush)
            qp.drawEllipse(QPointF(0,0), cs, cs)

            #Target velocity
            td = (cw/40)
            qp.translate(-cs/2.4,-cs*self.targ_velocities[i])
            qp.setPen(Qt.PenStyle.NoPen)
            qp.setBrush(QBrush(foreground_colour))
            qp.drawPolygon([QPointF(0,td),QPointF(0,-td),QPointF(sqrt(((td*2)**2)-(td/2)**2),0)])
            qp.translate(cs/2.4,cs*self.targ_velocities[i])

            if not self.config['wheel-lock']: qp.rotate(-self.wheel_rot[i])
            else: qp.rotate(self.base_rot)
            qp.translate(-irx,-iry)
        self.base_rot += 0.2
        if self.config['base-lock']: self.base_rot = 0

    def closeEvent(self, e):
        if config['general']['save-window-states']:
            self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        e.accept()