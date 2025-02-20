# import stuff
import sys, os, random, time, toml
from math import *
# pyqt6
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel

def resource_path(relative_path):
    # absolute file paths
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# setup variables
start_time = time.time()
title = 'QuickStatus'
refresh = 10
# statuses for testing only, recieve data later
things = ["thingamajig", "this is the end for me", "i woke up fresh as hell on a monday", "whatchamacallit", "among Gus", "blah blah blah the mitochondria is the powerhouse of the cell", "what is good homies", "thingamajig 2", "whatchamacallit 2", "among Gus 2", "blah blah blah the mitochondria is the powerhouse of the cell 2", "what is good homies 2", "LOOK OUT FROM ABOVE!!!", "My name is Yoshikage Kira. I'm 33 years old. My house is in the northeast section of Morioh, where all the villas are, and I am not married. I work as an employee for the Kame Yu department stores, and I get home every day by 8 PM at the latest. I don't smoke, but I occasionally drink. I'm in bed by 11 PM, and make sure I get eight hours of sleep, no matter what. After having a glass of warm milk and doing about twenty minutes of stretches before going to bed, I usually have no problems sleeping until morning. Just like a baby, I wake up without any fatigue or stress in the morning. I was told there were no issues at my last check-up. I'm trying to explain that I'm a person who wishes to live a very quiet life. I take care not to trouble myself with any enemies, like winning and losing, that would cause me to lose sleep at night. That is how I deal with society, and I know that is what brings me happiness. Although, if I were to fight I wouldn't lose to anyone."]
values = [0, 4, 3, 3, 1, 1, 2, 2, 3, 3, 4, 4, 1, 0]
# colour values
accent_colour = QColor("#0779FF")
caution_colour = QColor("#FFC600")
warning_colour = QColor("#F7821B")
death_colour = QColor("#FF5257")
velocity_colour = QColor("#60DE36")
power_colour = QColor("#47AC25")

# setup app icon
for i in range(100):
    things.append("i am a new object")
    values.append(random.randrange(0,5))
path = resource_path('assets/icons/mac.png')

# create child windows
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        MainWindow.windows = 0
        self.widgets = []
        for i in range(len(config['windows']['widgets'])):
            window = config['windows']['widgets'][i]
            if len(window) > 1:
                temp_tabs = []
                for i in window: temp_tabs.append(i)
                PagesWindow.tablist = temp_tabs.copy()
                self.widgets.append(PagesWindow())
                if len(self.widgets):
                    self.widgets[-1].show()
            else:
                if window[0] == 'status': self.widgets.append(StatusWindow())
                if window[0] == 'robot': self.widgets.append(RobotStateWidget())
                if window[0] == 'claw': self.widgets.append(ClawStateWidget())

                if len(self.widgets): self.widgets[-1].show()
            MainWindow.windows += 1

        '''if config['status']['enabled']: self.w1.show()
        if config['tabs']['enabled']: self.w2.show()
        if config['robot']['enabled']: self.w3.show()
        if config['claw']['enabled']: self.w4.show()'''

        '''widget = QWidget()
        layout = QGridLayout(widget)

        widget_one = PaintWidget()
        # or
        # widget_one.setFixedSize(1000, 1000)
        # or
        # widget_one.setMinimumSize(1000, 1000)
        scroll = QScrollArea(widgetResizable=True)
        scroll.setWidget(widget_one)

        layout.addWidget(scroll, 0, 0)
        # layout.addWidget(WidgetTwo(), 1, 1)
        self.setCentralWidget(widget)
        self.resize(w, h)'''

# status lights as widget in window
class StatusWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('QuickStatus', str(MainWindow.windows))

        restoreWindow(self)
        
        self.name = "status"

        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        scroll = QScrollArea(widgetResizable=True)
        scroll.setWidget(StatusIndicatorWidget())
        layout.addWidget(scroll, 0, 0)
        self.setLayout(layout)

        self.setWindowTitle(title + ' Status Indicators')

    def closeEvent(self, e):
        if config['windows']['save-window-positions']:
            self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        e.accept()

# restore window positions
def restoreWindow(self):
    windowScreenGeometry = self.settings.value( "windowScreenGeometry" )
    if windowScreenGeometry and config['windows']['save-window-positions']:
            self.restoreGeometry(windowScreenGeometry)
    else:
        self.resize(640, 480)

# create window with tabs
class PagesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('QuickStatus', str(MainWindow.windows))

        restoreWindow(self)

        # create tab widget
        widget = QWidget()
        self.layout = QGridLayout(widget)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(getattr(self.tabs.TabPosition, config['tabs']['align']))

        margins = {
            'North': [0,11,0,0],
            'East': [0,0,6,0],
            'South': [0,0,0,6],
            'West': [6,0,0,0]
        }
        margin = margins.get(config['tabs']['align'])
        self.layout.setContentsMargins(margin[0], margin[1], margin[2], margin[3])
        
        # create tabs
        for i in self.tablist:
            if i == 'claw': self.ClawTab()
            if i == 'robot': self.RobotStateTab()
            if i == 'status': self.StatusTab()

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.setWindowTitle(title + ' Tabs')

    def RobotStateTab(self):
        self.tabs.addTab(RobotStateWidget(), "Robot State")
    def StatusTab(self):
        self.tabs.addTab(StatusWindow(), "Status Lights")
    def ClawTab(self):
        self.tabs.addTab(ClawStateWidget(), "Claw State")

    def closeEvent(self, e):
        if config['windows']['save-window-positions']:
            self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        e.accept()
    def changeEvent(self, e):
        hl = app.palette().color(QPalette.ColorRole.WindowText)
        hl.setAlpha(25)
        hl = hl.name().strip('#')
        align_css = {
            'North': 'top',
            'East': 'right',
            'South': 'bottom',
            'West': 'left'
        }
        alignment = align_css.get(config['tabs']['align'])
        self.tabs.setStyleSheet(
        f"""
        QTabWidget::pane {{
            border-{alignment}: 1px solid;
            border-color: #33{hl};
            margin-{alignment}: 5px;
        }}
        """)

#create window with status lights
class StatusIndicatorWidget(QWidget):
    def __init__(self, parent=None):
        super(StatusIndicatorWidget, self).__init__(parent)
        self.num_circles = len(things)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(refresh)

    # scrolling setup
    def minimumSizeHint(self):
        if config['status']['scroll-horizontal'] == False: minX = 0
        else: minX = 100000
        if config['status']['scroll-vertical'] == False: minY = 0
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
        blink_speed = config['status']['blink-speed']
        ctime = (time.time() - start_time) % 10

        for i in range(self.num_circles):
            x = 4
            y = (i * 20) + 4
            radius = 13

            pen = QPen(dark)
            qp.setPen(pen)

            flash_time = 100
            if values[i] == 1: 
                current_colour = accent_colour
            if values[i] == 2: 
                current_colour = caution_colour
            if values[i] == 3: 
                current_colour = warning_colour
            if values[i] == 4: 
                current_colour = death_colour
                flash_time = blink_speed
            

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
            font.setPointSize(12)
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

class RobotStateWidget(QWidget):
    def __init__(self, parent=None):
        super(RobotStateWidget, self).__init__(parent)
        self.settings = QSettings('QuickStatus', str(MainWindow.windows))
        self.setWindowTitle(title + ' Robot State')
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
            if not config['robot']['wheel-lock']: qp.rotate(self.wheel_rot[i])
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

            if not config['robot']['wheel-lock']: qp.rotate(-self.wheel_rot[i])
            else: qp.rotate(self.base_rot)
            qp.translate(-irx,-iry)
        self.base_rot += 0.2
        if config['robot']['base-lock']: self.base_rot = 0

    def closeEvent(self, e):
        if config['windows']['save-window-positions']:
            self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        e.accept()

class ClawStateWidget(QWidget):
    def __init__(self, parent=None):
        super(ClawStateWidget, self).__init__(parent)
        self.settings = QSettings('QuickStatus', str(MainWindow.windows))
        self.setWindowTitle(title + ' Claw State')
        self.resize(500,500)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(refresh)
        claw = open(resource_path('assets/claw/claw.coords'))
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
        background_colour = palette.color(QPalette.ColorRole.Window)
        foreground_colour = palette.color(QPalette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        colour_chart = [foreground_colour, accent_colour, caution_colour, warning_colour, death_colour]
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
        if config['windows']['save-window-positions']:
            self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        e.accept()

if __name__ == '__main__':

    # config
    try:
        config = open(resource_path("assets/config.toml"))
        config.close()
    except:
        print("no config file found. making one for you 🥰")
        config = open(resource_path("assets/config.toml"), "w")
        #setup default values
        config.write('''[windows]
    save-window-positions = true
    widgets = [ ['status'], ['robot', 'claw'] ]
    data-rate = 5
    
[tabs]
    align = 'South' # Align tab bar to either 'North', 'East', 'South', or 'West'

[status]
    scroll-horizontal = false
    scroll-vertical = true
    blink-speed = 0.75 # Blink speed in seconds

[robot]
    base-lock = false
    wheel-lock = false

[claw]
    update-rate = 100 # Widget refresh rate in Hz''')
        config.close()

    with open(resource_path('assets/config.toml'), 'r') as fa:
        config = toml.load(fa)
    #print(toml.dump(['test',['test2','test3']]) as )

    # pyqt stuff
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(path))
    if sys.platform == 'win32': app.setStyle('Fusion')
    ex = MainWindow()
    #ex.show()
    sys.exit(app.exec())