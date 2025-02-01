# auto import stuff
import sys, os, random, time
from shutil import which
from math import *
import PyQt6
can_run = True
pip = which('pip') is not None
install_toml = ""
install_pyqt6 = ""

# toml
try: import toml
except:
    if pip == False:
        print('Missing toml module, can\'t install because you don\'t have pip\nhttps://pip.pypa.io/en/stable/installation/')
        sys.exit()
    while not (install_toml.capitalize() == "Y" or install_toml.capitalize() == "N"):
        install_toml = input("You don't have the toml module installed! Install it now? (Y/n) ")
    if install_toml.capitalize() == "Y":
        os.system('pip install toml')
        import toml
    else:
        can_run = False
# pyqt6
try:
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtWidgets import *
    from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
    from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
except:
    if pip == False:
        print('Missing PyQt6 module, can\'t install because you don\'t have pip\nhttps://pip.pypa.io/en/stable/installation/')
        sys.exit()
    while not (install_pyqt6.capitalize() == "Y" or install_pyqt6.capitalize() == "N"):
        install_pyqt6 = input("You don't have the PyQt6 module installed! Install it now? (Y/n) ")
    if install_pyqt6.capitalize() == "Y":
        os.system('pip install pyqt6')
        os.system('python3 pyqt.py') # restart program, pyqt6 breaks when trying to import after installation for some reason
        sys.exit()
    else:
        can_run = False

if can_run == False:
    print("mf really neglected to install the modules i NEED to run. shutting the whole operation down.")
    sys.exit()

# setup variables
start_time = time.time()
w = 640; h = 480
title = 'QuickStatus'
# statuses for testing only, recieve data later
things = ["thingamajig", "this is the end for me", "i woke up fresh as hell on a monday", "whatchamacallit", "among Gus", "blah blah blah the mitochondria is the powerhouse of the cell", "what is good homies", "thingamajig 2", "whatchamacallit 2", "among Gus 2", "blah blah blah the mitochondria is the powerhouse of the cell 2", "what is good homies 2", "LOOK OUT FROM ABOVE!!!", "My name is Yoshikage Kira. I'm 33 years old. My house is in the northeast section of Morioh, where all the villas are, and I am not married. I work as an employee for the Kame Yu department stores, and I get home every day by 8 PM at the latest. I don't smoke, but I occasionally drink. I'm in bed by 11 PM, and make sure I get eight hours of sleep, no matter what. After having a glass of warm milk and doing about twenty minutes of stretches before going to bed, I usually have no problems sleeping until morning. Just like a baby, I wake up without any fatigue or stress in the morning. I was told there were no issues at my last check-up. I'm trying to explain that I'm a person who wishes to live a very quiet life. I take care not to trouble myself with any enemies, like winning and losing, that would cause me to lose sleep at night. That is how I deal with society, and I know that is what brings me happiness. Although, if I were to fight I wouldn't lose to anyone."]
values = [0, 4, 3, 3, 1, 1, 2, 2, 3, 3, 4, 4, 1, 0]

# setup app icon
for i in range(100):
    things.append("i am a new object")
    values.append(random.randrange(0,5))
if sys.platform == "darwin":
    print("mac detected, becoming tim apple")
    path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'assets/icons/mac.png')
elif sys.platform == "win32":
    print("windows detected, becoming annoying")
    path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'assets/icons/generic.png')
else:
    print("linux (probably) detected, hacking mainframe")
    path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'assets/icons/generic.png')

# save window positions
def SavePosition(window):
    name = window.name

    width = window.size().width()
    height = window.size().height()
    x = window.pos().x()
    y = window.pos().y()

    config[name]['width'] = width
    config[name]['height'] = height
    config[name]['x'] = x
    config[name]['y'] = y
    with open('assets/config.toml', 'w') as f:
        toml.dump(config, f)

# create child windows
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.w1 = StatusWindow()
        self.w2 = PagesWindow()

        if config['status']['enabled']: self.w1.show()
        if config['tabs']['enabled']: self.w2.show()

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
        self.settings = QSettings('QuickStatus', 'Status')

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
        self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        e.accept()

# restore window positions
def restoreWindow(self):
    windowScreenGeometry = self.settings.value( "windowScreenGeometry" )
    if windowScreenGeometry and config['general']['save-window-positions']:
            self.restoreGeometry(windowScreenGeometry)
    else:
        self.resize(640, 480)

# create window with tabs
class PagesWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings('QuickStatus', 'Pages')

        restoreWindow(self)

        widget = QWidget()
        self.layout = QGridLayout(widget)
        #layout.setContentsMargins(0,0,0,0)
        '''page = 1
        max_page = 1
        text = QLabel("Page " + str(page) + "/" + str(max_page))
        text.setAlignment(Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(text,0,0)
        next_page = QPushButton("Next Page")
        last_page = QPushButton("Last Page")
        layout.addWidget(next_page,0,2, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(last_page,0,1, Qt.AlignmentFlag.AlignBottom)'''
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(self.tabs.TabPosition.South)

        self.tab1UI()
        self.tab2UI()

        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

        self.setWindowTitle(title + ' Tabs')

    def tab1UI(self):
        self.tab1 = QPushButton("Blow up all the BMW showrooms in britain")
        self.tab1.clicked.connect(self.destruct)
        self.tabs.addTab(self.tab1, "Self Destruction")
    def tab2UI(self):
        self.tab2 = StatusWindow()
        self.tabs.addTab(self.tab2, "Dumbass status lights")
    def destruct(self):
        sys.exit()

    def closeEvent(self, e):
        self.settings.setValue( "windowScreenGeometry", self.saveGeometry() )
        e.accept()

#create window with status lights
class StatusIndicatorWidget(QWidget):
    def __init__(self, parent=None):
        super(StatusIndicatorWidget, self).__init__(parent)
        self.num_circles = len(things)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
        accent_colour = QColor("#0779FF")
        caution_colour = QColor("#FFC600")
        warning_colour = QColor("#F7821B")
        death_colour = QColor("#FF5257")
        background_colour = palette.color(QPalette.ColorRole.Window)
        foreground_colour = palette.color(QPalette.ColorRole.Text)
        dark = palette.color(QPalette.ColorRole.Mid)
        flash_time = 100
        qp.setPen(foreground_colour)
        size = self.size()
        width = size.width()
        height = size.height()
        qp.fillRect(self.rect(), QColor(background_colour))
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

if __name__ == '__main__':

    # config
    try:
        config = open("assets/config.toml")
        config.close()
    except:
        print("no config file found. making one for you 🥰")
        config = open("assets/config.toml", "w")
        #setup default values
        config.write('''[general]
                     [status]
                     [tabs]''')
        config.close()
        with open('assets/config.toml', 'r') as f:
            config = toml.load(f)
        
        config['general']['save-window-positions'] = True
        
        config['status']['enabled'] = True
        config['status']['scroll-horizontal'] = False
        config['status']['scroll-vertical'] = True
        config['status']['blink-speed'] = 0.75

        config['tabs']['enabled'] = True

        with open('assets/config.toml', 'w') as f:
            toml.dump(config, f)

    with open('assets/config.toml', 'r') as f:
        config = toml.load(f)

    # pyqt stuff
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(path))
    app.setApplicationName("Fart")
    if sys.platform == 'win32': app.setStyle('Fusion')
    ex = MainWindow()
    #ex.show()
    sys.exit(app.exec())