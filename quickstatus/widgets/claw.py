from utils.imports import *
from utils.generic import closeEvent, restoreWindow, colours, widget_refresh

class ClawWidget(QWidget):
    def __init__(self, wid):
        super(ClawWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))

        restoreWindow(self)

        self.setWindowTitle('QuickStatus (Claw State)')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        claw = open('resources/widgets/claw/claw.coords')
        self.clawv = []
        clawl = []
        b = 0
        for i in claw:
            clawl.append(i.strip("\n"))
            self.clawv.append(QPointF(float(clawl[b].split(", ")[0]), float(clawl[b].split(", ")[1])))
            b += 1
        claw.close()

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
        colour_chart = [foreground_colour, colours.accent_colour, colours.caution_colour, colours.warning_colour, colours.death_colour]
        size = self.size()
        w = size.width()
        h = size.height()
        cw = w/2 # canvas width
        ch = h/2 # canvas height

        qp.setBrush(foreground_colour)
        qp.setPen(QPen(foreground_colour, 8))
        qp.save()
        claw = QPolygonF(self.clawv)

        scale = cw/500

        irx1 = 100*-0.5
        iry1 = 300*-0.5
        self.arm = 45
        self.elev1 = 0
        self.elev2 = 1
        self.elev3 = 0.73
        
        # arm
        qp.scale(scale,scale)
        qp.translate(cw/scale,ch/scale)
        qp.translate(0,-self.elev2*500+500-self.elev3*500)
        qp.rotate(self.arm)
        qp.translate(irx1,iry1*2) # rotate from middle bottom
        qp.drawPolygon(claw)
        qp.setPen(QPen(foreground_colour, 8))
        qp.setBrush(background_colour)
        qp.drawEllipse(QPointF(-irx1,-iry1*2),25,25)
        qp.drawEllipse(QPointF(-irx1,-iry1*2),4,4)

        qp.restore()
        qp.save()
        # arm line
        qp.setPen(QPen(background_colour, 16))
        qp.scale(scale,scale)
        qp.translate(cw/scale,ch/scale)
        qp.translate(0,-self.elev2*500+500-self.elev3*500)
        qp.drawLine(QLineF(-100,0,100,0))
        qp.setPen(QPen(foreground_colour, 8))
        qp.drawLine(QLineF(-100,0,100,0))

        # elevators
        qp.restore()
        qp.setBrush(Qt.BrushStyle.NoBrush)
        qp.scale(scale,scale)
        qp.translate(cw/scale,ch/scale)
        qp.translate(0,-self.elev1*500)
        qp.drawRoundedRect(QRectF(-125,-25,250,550), 0,0)
        qp.translate(0,-self.elev2*500)
        qp.drawRoundedRect(QRectF(-100,0,200,500), 0,0)

    def closeEvent(self, e):
        closeEvent(self, e)