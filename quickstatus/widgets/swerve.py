from quickstatus.utils.imports import *
from quickstatus.utils.generic import restoreWindow, closeEvent, widget_refresh, colours, config
from quickstatus.utils.network_tables import datatable, NetworkTables
from math import degrees

class SwerveWidget(QWidget):
    def __init__(self, wid, conf):
        super(SwerveWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        self.setWindowTitle('QuickStatus (Swerve State)')

        # Adjust the timer interval to match the monitor's refresh rate
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.base_rot = 0
        self.wheel_rot = [0,0,0,0]
        self.velocities = [1,1,1,1]
        self.targ_velocities = [0,0,0,0]
        self.powers = [0.5,0.5,0.5,0.5]
        self.wheel_status = [1,1,1,1]
        self.base_status = 0
    # draw status lights
    def paintEvent(self, event):
        #Setup
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
        rs = w*0.25 # box size
        cs = w*0.12 # circle radius

        base = datatable[config['swerve']['base-table']]
        wheels = datatable[config['swerve']['wheel-table']]

        if NetworkTables.inst.isConnected() and 'module_positions' in wheels and 'odometry_pose' in base:
            base = base['odometry_pose']
            wheels = wheels['module_positions']
            if not self.config['base-lock']: self.base_rot = -degrees(base[2])
            else: self.base_rot = 0
            if not self.config['wheel-lock']: self.wheel_rot = wheels
            else: self.wheel_rot = [0,0,0,0]

            # Rotate base
            qp.translate(cw,ch)
            if not self.config['base-lock']: qp.rotate(self.base_rot)

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
                if i%2: irx = -irx1
                else: irx = irx1
                if i>1: iry = -iry1
                else: iry = iry1
                qp.translate(irx,iry)
                if not self.config['wheel-lock']: qp.rotate(self.wheel_rot[i])
                else: qp.rotate(-self.base_rot)
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
                
                qp.setPen(QPen(colours.velocity_colour, bd, cap=Qt.PenCapStyle.FlatCap))
                qp.drawLine(QLineF(-bd2, 0, -bd2, -cs*self.velocities[i]))
                
                qp.setPen(QPen(colours.power_colour, bd, cap=Qt.PenCapStyle.FlatCap))
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
                qp.drawPolygon([QPointF(0,td),QPointF(0,-td),QPointF(td*1.5,0)])
                qp.translate(cs/2.4,cs*self.targ_velocities[i])

                if not self.config['wheel-lock']: qp.rotate(-self.wheel_rot[i])
                else: qp.rotate(self.base_rot)
                qp.translate(-irx,-iry)
            if self.config['base-lock']: self.base_rot = 0
        else:
            qp.setPen(foreground_colour)
            font = QFont()
            font.setPointSizeF(16)
            qp.setFont(font)
            text = "NetworkTable not connected"
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(text)/2
            text_height = font_metrics.height()
            qp.drawText(QPointF(cw-text_width, ch+text_height/4), text)
            self.setMinimumHeight(text_height)

    def closeEvent(self, e):
        closeEvent(self, e)