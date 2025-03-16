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

def getAngleLine(x: float, y: float, angle: float, dist: float):
    angle_rad = radians(angle)
    a = dist * sin(angle_rad) + x
    b = -dist * cos(angle_rad) + y

    return QLineF(x,y,a,b)

def getAngleLineFromPoint(point: QPoint, angle: float, dist: float):
    angle_rad = radians(angle)
    a = dist * sin(angle_rad) + point.x()
    b = -dist * cos(angle_rad) + point.y()

    return QLineF(point,QPointF(a,b))

class ReefWidget(QWidget):
    def __init__(self, wid, conf):
        super(ReefWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        self.setWindowTitle('QuickStatus (Reef)')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.old_dt = int(monotonic()*150)
        self.wr = 0
        self.rot_right = True

        selected_file = open('resources/widgets/reef/selected.coords')
        reef_file = open('resources/widgets/reef/reef.coords')
        points_file = open('resources/widgets/reef/points.coords')
        self.selected = []
        self.reef = []
        self.reef_points = []
        scaling = 4
        temp_list = []
        b = 0
        for i in selected_file:
            temp_list.append(i.strip("\n"))
            self.selected.append(QPointF(float(temp_list[b].split(", ")[0]), float(temp_list[b].split(", ")[1])))
            b += 1
        temp_list = []
        b = 0
        for i in reef_file:
            temp_list.append(i.strip("\n"))
            self.reef.append(QPointF(float(temp_list[b].split(", ")[0])*scaling, float(temp_list[b].split(", ")[1])*scaling))
            b += 1
        temp_list = []
        b = 0
        for i in points_file:
            temp_list.append(i.strip("\n"))
            self.reef_points.append(QPointF(float(temp_list[b].split(", ")[0])*scaling, float(temp_list[b].split(", ")[1])*scaling))
            b += 1
        self.selected = self.selected[:-1]
        self.reef = self.reef[:-1]
        self.reef_points = self.reef_points[:-1]
        selected_file.close()
        reef_file.close()
        points_file.close()

        self.ab = 0
        self.nt_connected = False

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        palette = self.palette()
        foreground_colour = palette.color(palette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        if sys.platform == 'darwin': palette.setColor(QPalette.ColorRole.Window, dark)
        background_colour = self.palette().color(self.palette().ColorRole.Window)
        reef_colour = QColor("#E900FF")
        self.setPalette(palette)
        colour_chart = [foreground_colour, colours.accent_colour, colours.caution_colour, colours.warning_colour, colours.death_colour]
        size = self.size()
        w = size.width()
        h = size.height()
        cw = w/2 # canvas width
        ch = h/2 # canvas height
        dt = int(monotonic()*150)

        table = datatable['SmartDashboard']
        table_req = []
        if self.nt_connected == False:
            self.nt_connected = all(k in table for k in table_req)

        if NetworkTables.inst.isConnected() and self.nt_connected:
            qp.setBrush(Qt.BrushStyle.NoBrush)
            qp.setPen(QPen(reef_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            scale = cw/600
            qp.scale(scale,scale)
            qp.translate(cw/scale-450,ch/scale+160)

            exl = 130 # extend length
            exl2 = 225 # lower extend length
            arcs = 24*3 # arc size
            arca = 53 # arc angle
            arca16 = arca*16 # arc angle *16
            rh = 300 # reef height

            self.ab += 0.01
            selected = round(self.ab) % 4 + 1
            is_flashing = dt/50 % 1 <= 0.5

            if selected == 2:
                if is_flashing:
                    qp.setPen(QPen(colours.accent_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
                    qp.drawPolygon(QPolygonF(self.selected).translated(getAnglePoint(0,rh/1.5,arca,exl2)))
                qp.setPen(QPen(foreground_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            qp.drawLine(getAngleLine(0,rh/1.5,arca, exl2))
            qp.setPen(QPen(reef_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))

            if selected == 3:
                if is_flashing:
                    qp.setPen(QPen(colours.accent_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
                    qp.drawPolygon(QPolygonF(self.selected).translated(getAnglePoint(0,-rh/4,arca,exl2)))
                qp.setPen(QPen(foreground_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            qp.drawLine(getAngleLine(0,-rh/4,arca, exl2))
            qp.setPen(QPen(reef_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))

            endPoint = getAnglePoint(0,-rh-arcs/2,arca,arcs/2+exl)
            anglePoint = getAnglePoint(0,0,90+arca,arcs)
            point_3 = QPointF(endPoint.x()-anglePoint.x()+arcs-1, 
                                 endPoint.y()-anglePoint.y()+1-exl)
            
            if selected == 4:
                if is_flashing:
                    qp.setPen(QPen(colours.accent_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
                    qp.drawPolygon(QPolygonF(self.selected).translated(point_3))
                qp.setPen(QPen(foreground_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            qp.drawLine(QPointF(endPoint.x()-anglePoint.x()+arcs-1, 
                                 endPoint.y()-anglePoint.y()+1),
                       point_3)
            qp.setPen(QPen(reef_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))

            qp.drawLine(0,rh, 0,-rh)
            
            qp.drawArc(0,-rh-arcs,
                       arcs*2,arcs*2,
                       2880,-arca16)

            qp.drawLine(getAnglePoint(0,-rh-arcs/2,arca,arcs/2),
                        getAnglePoint(0,-rh-arcs/2,arca,arcs/2+exl))
            
            
            qp.drawArc(QRectF(QPointF(endPoint.x()-anglePoint.x()-arcs-1, 
                                      endPoint.y()-anglePoint.y()-arcs+1),
                              QSizeF(arcs*2,
                                     arcs*2)),
                       0,-arca16)
            
            # top-down
            td_selected = round(self.ab) % 13
            qp.translate(650,0)
            QPointF()
            for i in range(len(self.reef_points)):
                index = self.reef_points[i]
                branch_point = getAnglePointFromPoint(index,60*floor(i/2),125)
                if i+1 == td_selected:
                    if is_flashing:
                        qp.setPen(QPen(colours.accent_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
                        qp.drawPolygon(QPolygonF(self.selected).translated(branch_point))
                    qp.setPen(QPen(foreground_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
                qp.drawLine(index,branch_point)
                qp.setPen(QPen(reef_colour, 24, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin))
            qp.drawPolygon(self.reef)

            place_level = "L"+str(selected)
            font = QFont('Iosevka Aile')
            font.setBold(True)
            font.setPixelSize(160)
            ls_width = QFontMetrics(font).horizontalAdvance(place_level)
            qp.setFont(font)
            qp.setPen(foreground_colour)
            qp.drawText(QPointF(0-ls_width/2,-500),place_level)

        else: noNetworkTable(self)