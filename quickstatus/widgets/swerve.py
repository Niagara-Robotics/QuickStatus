from quickstatus.utils.imports import *
from quickstatus.utils.generic import *
from quickstatus.utils.network_tables import datatable, NetworkTables
from math import degrees

class SwerveWidget(QWidget):
    name = 'Swerve'
    def __init__(self, wid, conf):
        super(SwerveWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        # Adjust the timer interval to match the monitor's refresh rate
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.velocities = [0,0,0,0]
        self.targ_velocities = [0,0,0,0]
        self.powers = [0,0,0,0]
        self.wheel_status = [1,1,1,1]
        self.base_status = 0

    def resizeEvent(self, event):
        self.width_cache = self.width()
        self.height_cache = self.height()
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        # setup canvas & variables
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨

        cw, ch = self.width_cache/2, self.height_cache/2 # centre width, centre height
        self.base_size = 360
        self.wheel_size = 90

        # ensure NetworkTable data exists
        base_table = datatable[self.config['base-table']]
        wheels_table = datatable[self.config['wheel-table']]
        
        if NetworkTables.inst.isConnected():
            scale = cw/400
            qp.scale(scale,scale)
            qp.translate(cw/scale,ch/scale)

            # setup config and NetworkTable data
            self.check_data(base_table, wheels_table)

            self.front_size = self.base_size/3
            self.base_x = self.base_size*-0.5
            self.base_y = self.base_x

            self.wheel_positions = [
                (self.base_x, self.base_y), 
                (-self.base_x, self.base_y),
                (self.base_x, -self.base_y),
                (-self.base_x, -self.base_y)
            ]
            
            base_lock = self.config['base-lock']
            wheel_lock = self.config['wheel-lock']
            
            if self.base is not None: 
                self.base_rot = -degrees(self.base) if not base_lock else 0
                qp.rotate(self.base_rot)

                self.draw_base(qp)

            if self.wheels is not None: 
                self.wheel_rot = self.wheels if not wheel_lock else [0, 0, 0, 0]
                self.draw_wheels(qp)

        else: noNetworkTable(self)
    
    def setup_palette(self):
        palette = self.palette()
        self.foreground_colour = palette.color(palette.ColorRole.Text)
        self.foreground_colour.setAlpha(255)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        if sys.platform == 'darwin': palette.setColor(QPalette.ColorRole.Window, dark)
        self.setPalette(palette)
        self.background_colour = palette.color(palette.ColorRole.Window)
        self.colour_chart = [self.foreground_colour, Colours.accent_colour, Colours.caution_colour, Colours.warning_colour, Colours.death_colour]
    
    def check_data(self, base, wheels):
        try: self.base = base['odometry_pose'][2]
        except: self.base = None

        try: self.wheels = wheels['module_positions']
        except: self.wheels = None
    
    def draw_base(self, qp:QPainter):
        qp.setPen(QPen(self.colour_chart[self.base_status], 7))
        qp.setBrush(Qt.BrushStyle.NoBrush)
        qp.drawRect(QRectF(self.base_x, self.base_y, self.base_size, self.base_size))
        qp.fillRect(QRectF(self.base_x, self.base_y, self.base_size, self.front_size), QBrush(self.colour_chart[self.base_status]))
    
    def draw_wheels(self, qp:QPainter):
        for i in range(4):
            wheel_x, wheel_y = self.wheel_positions[i]
            qp.translate(wheel_x, wheel_y)
            qp.rotate(self.wheel_rot[i])

            self.draw_wheel_outline(qp)
            self.draw_gauge_marks(qp)
            self.draw_velocity(qp, 50, self.velocities[i], self.powers[i])
            self.draw_wheel_circle(qp, self.wheel_status[i])
            self.draw_target_velocity(qp, 10, self.targ_velocities[i])

            qp.rotate(-self.wheel_rot[i])
            qp.translate(-wheel_x, -wheel_y)
    
    def draw_wheel_outline(self, qp:QPainter):
        qp.setPen(QPen(self.background_colour, 22))
        qp.setBrush(self.background_colour)
        qp.drawEllipse(QPoint(0,0),self.wheel_size,self.wheel_size)
    
    def draw_gauge_marks(self, qp:QPainter):
        self.foreground_colour.setAlpha(150)
        qp.setPen(QPen(self.foreground_colour, 4))
        self.foreground_colour.setAlpha(255)
        qp.setBrush(Qt.BrushStyle.NoBrush)
        qp.drawLine(QLineF(-self.wheel_size/2.4, 0, self.wheel_size/2.4, 0))
        qp.drawLine(QLineF(-self.wheel_size/2.4, -self.wheel_size/2, self.wheel_size/2.4, -self.wheel_size/2))
        qp.drawLine(QLineF(-self.wheel_size/2.4, self.wheel_size/2, self.wheel_size/2.4, self.wheel_size/2))
    
    def draw_velocity(self, qp:QPainter, bar_width:int, velocity:float, power:float):
        bd = bar_width/2
        bd2 = bd/2
        qp.setPen(QPen(self.foreground_colour, 6))
        qp.setBrush(Qt.BrushStyle.NoBrush)

        qp.drawChord(QRectF(-self.wheel_size,-self.wheel_size,self.wheel_size*2,self.wheel_size*2),(bar_width*8)+(1440),((180-bar_width)*16))
        qp.drawChord(QRectF(-self.wheel_size,-self.wheel_size,self.wheel_size*2,self.wheel_size*2),(-bar_width*8)+(1440),(-(180-bar_width)*16))
        
        qp.setPen(QPen(Colours.velocity_colour, bd, cap=Qt.PenCapStyle.FlatCap))
        qp.drawLine(QLineF(-bd2, 0, -bd2, -self.wheel_size*velocity))
        
        qp.setPen(QPen(Colours.power_colour, bd, cap=Qt.PenCapStyle.FlatCap))
        qp.drawLine(QLineF(bd2, 0, bd2, -self.wheel_size*power))
    
    def draw_wheel_circle(self, qp:QPainter, status:int):
        qp.setPen(QPen(self.colour_chart[status], 7))
        qp.setBrush(Qt.BrushStyle.NoBrush)
        qp.drawEllipse(QPoint(0,0), self.wheel_size, self.wheel_size)

    def draw_target_velocity(self, qp:QPainter, tri_size:int, target_velocity:float):
        translate = QPointF(-self.wheel_size/2.4, -self.wheel_size*target_velocity)
        qp.setPen(Qt.PenStyle.NoPen)
        qp.setBrush(self.foreground_colour)
        qp.drawPolygon(QPolygonF([QPointF(0, tri_size), QPointF(0, -tri_size), QPointF(tri_size*1.5, 0)]).translated(translate))