from quickstatus.utils.imports import *
from quickstatus.utils.generic import *
from quickstatus.utils.network_tables import datatable, NetworkTables
from math import sin, cos, radians, floor

def getAnglePoint(x: float, y: float, angle: float, dist: float):
    angle_rad = radians(angle)
    a = dist * sin(angle_rad) + x
    b = -dist * cos(angle_rad) + y

    return QPointF(a,b)
def getAnglePointFromPoint(point: QPoint, angle: float, dist: float):
    angle_rad = radians(angle)
    a = dist * sin(angle_rad) + point.x()
    b = -dist * cos(angle_rad) + point.y()

    return QPointF(QPointF(a,b))

def getAngleLineFromPoint(point: QPoint, angle: float, dist: float):
    angle_rad = radians(angle)
    a = dist * sin(angle_rad) + point.x()
    b = -dist * cos(angle_rad) + point.y()

    return QLineF(point,QPointF(a,b))

class ReefWidget(QWidget):
    name = 'Reef'
    def __init__(self, wid, conf):
        super(ReefWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        self.base_width = 1150
        self.base_height = 1150

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.ab = 0
        
        self.load_coordinates()

        self.global_font = global_config.data['general']['global_font']

    def load_coordinates(self):
        scaling = 4
        self.selected = []
        self.reef = []
        self.reef_points = []

        with open('resources/widgets/reef/selected.coords') as selected_file, \
             open('resources/widgets/reef/reef.coords') as reef_file, \
             open('resources/widgets/reef/points.coords') as points_file:
            self.selected = self._parse_coordinates(selected_file)
            self.reef = self._parse_coordinates(reef_file, scaling)
            self.reef_points = self._parse_coordinates(points_file, scaling)

    def _parse_coordinates(self, file, scaling=1.0):
        return [
            QPointF(float(x) * scaling, float(y) * scaling)
            for line in file
            if (coords := line.strip().split(", ")) and len(coords) == 2
            for x, y in [coords]
        ]
    
    def resizeEvent(self, event):
        resize_window(self)
    
    def changeEvent(self, event):
        self.setup_palette()

    def paintEvent(self, event):
        # setup canvas & variables
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)

        cw, ch = self.width_cache/2, self.height_cache/2 # centre width, centre height
        dt = int(monotonic() * 150)

        # ensure NetworkTable data exists
        table = datatable[self.config['network-table']]

        if NetworkTables.inst.isConnected():
            scale = self.scale
            qp.scale(scale,scale)
            qp.translate(cw/scale-450,ch/scale+160)

            self.ab += 0.01
            is_flashing = dt/50 % 1 <= 0.5
            selected = round(self.ab) % 4 + 1
            try: selected = round(table['coral_place_level'])
            except: selected = None

            if selected is not None: self.draw_branches(qp, 300, 130, 75, 53, is_flashing, selected)
            
            qp.translate(650, 0)
            if global_config.data['general']['show-unused-widgets']: self.draw_topdown(qp, is_flashing)
            else: qp.translate(0,350)

            if selected is not None: self.draw_place_text(qp, selected)

        else: noNetworkTable(self)

    def setup_palette(self):
        palette = self.palette()

        self.foreground_colour = palette.color(palette.ColorRole.Text)
        self.foreground_colour.setAlpha(255)

        self.reef_colour = QColor("#E900FF")
        
        self.setPalette(palette)
    
    def draw_branches(self, qp:QPainter, reef_height:float, branch_length:float, arc_size:float, arc_angle:float, is_flashing:bool, selected:int):
        # setup variables
        endPoint = getAnglePoint(0,-reef_height-arc_size/2,arc_angle,arc_size/2+branch_length)
        anglePoint = getAnglePoint(0,0,90+arc_angle,arc_size)
        point_3 = QPointF(endPoint.x()-anglePoint.x()+arc_size-1, 
                                endPoint.y()-anglePoint.y()+1-branch_length)
        long_branch_length = branch_length*1.7
        
        # draw coral placement slots
        self.draw_branch(qp, is_flashing, QPointF(0,reef_height/1.5), arc_angle, long_branch_length, 2==selected)
        self.draw_branch(qp, is_flashing, QPointF(0,-reef_height/4), arc_angle, long_branch_length, 3==selected)
        self.draw_high_branch(qp, is_flashing, point_3, arc_angle, branch_length, 4==selected)
        
        # draw main reef
        qp.setPen(QPen(self.reef_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
        qp.drawLine(0,reef_height, 0,-reef_height)
        
        qp.drawArc(0,-reef_height-arc_size,
                    arc_size*2,arc_size*2,
                    2880,-arc_angle*16)

        qp.drawLine(getAnglePoint(0,-reef_height-arc_size/2,arc_angle,arc_size/2),
                    getAnglePoint(0,-reef_height-arc_size/2,arc_angle,arc_size/2+branch_length))
        
        qp.drawArc(QRectF(QPointF(endPoint.x()-anglePoint.x()-arc_size-1, 
                                    endPoint.y()-anglePoint.y()-arc_size+1),
                            QSizeF(arc_size*2,
                                    arc_size*2)),
                    0,-arc_angle*16)
    
    def draw_branch(self, qp:QPainter, is_flashing:bool, point:QPointF, angle:float, extend_length:float, selected:bool):
        if selected: 
            self.draw_selected(qp, is_flashing, point, angle, extend_length)
            qp.setPen(QPen(self.foreground_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
        else: qp.setPen(QPen(self.reef_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))

        qp.drawLine(getAngleLineFromPoint(point, angle, extend_length))

    def draw_high_branch(self, qp:QPainter, is_flashing:bool, point:QPointF, arca:float, extend_length:float, selected:bool):
        # used only for top branch
        if selected: 
            self.draw_selected(qp, is_flashing, point, arca, 0)
            qp.setPen(QPen(self.foreground_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
        else: qp.setPen(QPen(self.reef_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))

        qp.drawLine(QPointF(point.x(), point.y()+extend_length),point)
        
    def draw_topdown(self, qp:QPainter, is_flashing:bool):
        # setup variables
        td_selected = round(self.ab) % 13
        td_selected = 1

        # draw branch lines
        for i in range(len(self.reef_points)):
            index = self.reef_points[i]
            branch_point = getAnglePointFromPoint(index,60*floor(i/2),125)
            if i+1 == td_selected:
                if is_flashing:
                    qp.setPen(QPen(Colours.accent_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
                    qp.drawPolygon(QPolygonF(self.selected).translated(branch_point))
                qp.setPen(QPen(self.foreground_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            qp.drawLine(index,branch_point)
            qp.setPen(QPen(self.reef_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
        
        # draw top-down view of reef shape
        qp.drawPolygon(self.reef)

    def draw_place_text(self, qp:QPainter, selected:int):
        # setup variables
        place_level = "L"+str(selected)
        font = QFont(self.global_font)
        font.setBold(True)
        font.setPixelSize(200)
        ls_width = QFontMetrics(font).horizontalAdvance(place_level)

        # draw text
        qp.setFont(font)
        qp.setPen(self.foreground_colour)
        qp.drawText(QPointF(0-ls_width/2,-450),place_level)

    def draw_selected(self, qp:QPainter, is_flashing:bool, point:QPointF, angle:float, extend_length:float):
        if is_flashing:
            qp.setPen(QPen(Colours.accent_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            if angle == 0: qp.drawPolygon(QPolygonF(self.selected).translated(point))
            else: qp.drawPolygon(QPolygonF(self.selected).translated(getAnglePointFromPoint(point, angle, extend_length)))