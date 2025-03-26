from itertools import count, islice
import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap

from numpy import linspace
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import serial
import can
import cantools
import os
import serial.tools.list_ports
from GUI.Styles.StyleSheet import style_sheet

import ctypes
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class CANCapture(QObject):
    V1_status = pyqtSignal(object)
    V2_status = pyqtSignal(object)
    TT_status = pyqtSignal(object)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    @pyqtSlot()
    def startThread(self):
        print("Thread started")

    @pyqtSlot(object, str, int, int)
    def startReceiving(self, tester):
        self._running = True
        print("Receiving started")
        while self._running:
            tester.flush_input()
            status_V1 = tester.expect('VESC_Status1_V1', None, timeout=.01, discard_other_messages=True)
            status_V2 = tester.expect('VESC_Status1_V1', None, timeout=.01, discard_other_messages=True)
            status_TT = tester.expect('TEENSY_Status', None, timeout=.01, discard_other_messages=True)
            if status_V1 is not None:
                self.V1_status.emit(status_V1)
            if status_V2 is not None:
                self.V2_status.emit(status_V2)
            if status_TT is not None:
                self.TT_status.emit(status_TT)
            QtCore.QThread.msleep(10)  # sleep for a short duration to prevent high CPU usage

class Window(QMainWindow):
    requestData = pyqtSignal(object, str, int, int)
    tabChanged = pyqtSignal(int)  # Signal to notify when a tab is changed

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        # Make it light theme
        self._thread = QThread()
        self._threaded = CANCapture()
        self._threaded.V1_status.connect(self.plotV1Graph)
        self._threaded.V2_status.connect(self.plotV2Graph)
        self._threaded.TT_status.connect(self.plotTTGraph)
        self.requestData.connect(self._threaded.startReceiving)
        self._thread.started.connect(self._threaded.startThread)
        self._threaded.moveToThread(self._thread)
        self.initializeUI()
        self.setupMenu()

        # Connect the aboutToQuit signal to the stopThread method
        QApplication.instance().aboutToQuit.connect(self.stopThread)

    def initializeUI(self):
        """Initialize the window and display its contents."""
        app.setStyle('WindowsVista')  # Replace 'Windows' with the desired style
        app.setWindowIcon(QtGui.QIcon('GUI/icon.svg'))
        self.showMaximized()
        self.setMinimumSize(800, 700)
        self.setWindowTitle('VESCdyno')
        self.setupWindow()
        self.show()

    def setupWindow(self):
        # Create the tools panel
        tools_panel = self.setupToolsPanel()

        # Create Live Plot panel
        self.live_plot = self.setupLivePlot()

        # Create Animation Window
        self.anim_dock = self.setAnimWindow()

        # Create Start Button
        button_layout = self.setupStartButton()
        self.button_widget = QWidget()
        self.button_widget.setLayout(button_layout)

        # Create a layout for the main window
        self.main_layout = QHBoxLayout()  # Use horizontal layout to place tools panel on the left
        self.graph_layout = QVBoxLayout()  # Vertical layout for the graph and buttons

        # Add tools_panel as a widget, not a layout
        self.graph_layout.addWidget(self.live_plot)
        self.graph_layout.addWidget(self.anim_dock)
        self.graph_layout.addWidget(self.button_widget)

        # Initialize results_label but hide it initially
        self.results_label = QLabel("results Layout")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_label.hide()  # Hide it initially
        self.graph_layout.addWidget(self.results_label)

        # Add the tools panel and graph layout to the main layout
        self.main_layout.addLayout(tools_panel)
        self.main_layout.addLayout(self.graph_layout)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # Connect the tabChanged signal
        self.tabChanged.connect(self.onTabChanged)

    def onTabChanged(self, index):
        """Handle tab changes in the tools panel."""
        for i in range(self.graph_layout.count()):
            item = self.graph_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.hide()

        if index == 0:  # "Motor Control" tab
            # Show the original layout
            self.live_plot.show()
            self.anim_dock.show()
            self.button_widget.show()

        elif index == 1:  # "Graph Settings" tab
            self.anim_dock.show()
            self.results_label.show()

    def setupLivePlot(self):
        # Create an instance of GraphicsLayoutWidget
        win = pg.GraphicsLayoutWidget()

        # Apply the stylesheet to the GraphicsLayoutWidget
        win.setStyleSheet(style_sheet)

        # Dropdown
        self.dropdown1 = QComboBox()
        self.dropdown1.setFixedWidth(200)
        self.dropdown1.addItems(["MUT Current", "Option 2", "Option 3"])
        dropdown1_proxy = QtWidgets.QGraphicsProxyWidget()
        dropdown1_proxy.setWidget(self.dropdown1)
        win.addItem(dropdown1_proxy, row=0, col=1)

        self.dropdown2 = QComboBox()
        self.dropdown2.setFixedWidth(200)
        self.dropdown2.addItems(["Load motor RPM", "Option B", "Option C"])
        dropdown2_proxy = QtWidgets.QGraphicsProxyWidget()
        dropdown2_proxy.setWidget(self.dropdown2)
        win.addItem(dropdown2_proxy, row=1, col=1)

        self.dropdown3 = QComboBox()
        self.dropdown3.setFixedWidth(200)
        self.dropdown3.addItems(["Torque Transducer"])
        dropdown3_proxy = QtWidgets.QGraphicsProxyWidget()
        dropdown3_proxy.setWidget(self.dropdown3)
        win.addItem(dropdown3_proxy, row=2, col=1)

        # First plot
        self.p1 = win.addPlot(row=0, col=2)
        self.p1.getAxis('left').setPen(pg.mkPen(color='k', width=2))  # Black left axis with increased width
        self.p1.getAxis('bottom').setPen(pg.mkPen(color='k', width=2))  # Black bottom axis with increased width
        self.curve1 = self.p1.plot(pen=pg.mkPen(color='k', width=2))  # Black line with increased width

        # Second plot
        self.p2 = win.addPlot(row=1, col=2)
        self.p2.getAxis('left').setPen(pg.mkPen(color='k', width=2))  # Black left axis with increased width
        self.p2.getAxis('bottom').setPen(pg.mkPen(color='k', width=2))  # Black bottom axis with increased width
        self.curve2 = self.p2.plot(pen=pg.mkPen(color='k', width=2))  # Black line with increased width

        # Third plot
        self.p3 = win.addPlot(row=2, col=2)
        self.p3.getAxis('left').setPen(pg.mkPen(color='k', width=2))  # Black left axis with increased width
        self.p3.getAxis('bottom').setPen(pg.mkPen(color='k', width=2))  # Black bottom axis with increased width
        self.curve3 = self.p3.plot(pen=pg.mkPen(color='k', width=2))  # Black line with increased width

        self.windowWidth = 500  # width of the window displaying the curve

        self.Xm = linspace(0, 0, self.windowWidth)  # create array that will contain the relevant time series for plot
        self.ptr = -self.windowWidth
        self.Xm2 = linspace(0, 0, self.windowWidth)  # create array that will contain the relevant time series for plot
        self.ptr2 = -self.windowWidth
        self.Xm3 = linspace(0, 0, self.windowWidth)  # create array that will contain the relevant time series for plot
        self.ptr3 = -self.windowWidth
        return win
    

    def setAnimWindow(self):
        """Set up a window in the bottom-right corner to display the SVG."""
        anim_dock = QDockWidget()
        anim_dock.setWindowTitle("Setup Diagram")
        anim_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        # Disable movement but allow closing
        anim_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)

        # Load the image into a QLabel
        svg_label = QLabel()
        pixmap = QPixmap("GUI/Setup.png")
        pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        svg_label.setPixmap(pixmap)
        svg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the image within the label

        # Set the QLabel as the widget for the dock
        svg_container = QWidget()
        svg_layout = QVBoxLayout()
        svg_layout.addWidget(svg_label)
        svg_container.setLayout(svg_layout)
        anim_dock.setWidget(svg_container)

        # Set a fixed height for the dock widget
        anim_dock.setMinimumHeight(150)  # Adjust the height as needed
        anim_dock.setMaximumHeight(400)  # Adjust the height as needed

        # Add the dock widget to the bottom area
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, anim_dock)
        self.toggle_animation_act = anim_dock.toggleViewAction()

        return anim_dock
    
    def setupStartButton(self):
        # Add start button
        start_button = QPushButton("Start Thread")
        start_button.clicked.connect(self.startThread)

        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.stopThread)
        button_layout = QHBoxLayout()
        
        button_layout.addWidget(start_button)
        button_layout.addWidget(close_button)
        return button_layout
    
    def setupMenu(self):
        """Create a simple menu to manage the dock widget."""
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        # Create view menu and add actions
        view_menu = menu_bar.addMenu('View')
        view_menu.addAction(self.toggle_animation_act)

    def setupToolsPanel(self):
        """Set up a permanent tools panel with a QToolBox for motor control, graph settings, and data filters."""
        settings_toolbox = QToolBox()
        settings_toolbox.setFixedWidth(300)
        settings_toolbox.setCurrentIndex(0)  # Show the first tab by default

        # Tab 1: Motor Control
        motor_control_tab = QWidget()
        motor_control_layout = QVBoxLayout()
        motor_control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        MUT_current_label = QLabel("Motor 1 RPM:")
        MUT_current_box = QSpinBox()
        MUT_current_box.setRange(0, 1000)  # Set the range for RPM input
        MUT_current_box.setSingleStep(10)  # Set the step size for duty cycle input
        MUT_current_box.setValue(0)  # Set a default value

        load_rpm_label = QLabel("Motor 2 brake current:")
        load_rpm_input = QDoubleSpinBox()
        load_rpm_input.setRange(-5.0, 5.0)  # Set the range for duty cycle input
        load_rpm_input.setSingleStep(0.1)  # Set the step size for duty cycle input
        load_rpm_input.setValue(0)  # Set a default value

        motor_control_layout.addWidget(MUT_current_label)
        motor_control_layout.addWidget(MUT_current_box)
        motor_control_layout.addWidget(load_rpm_label)
        motor_control_layout.addWidget(load_rpm_input)

        motor_control_tab.setLayout(motor_control_layout)
        settings_toolbox.addItem(motor_control_tab, "Motor Control")

        # Tab 2: Graph Settings
        graph_settings_tab = QWidget()
        graph_settings_layout = QVBoxLayout()
        graph_settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        show_grid_cb = QCheckBox("Show Grid")
        show_grid_cb.setChecked(True)

        show_legend_cb = QCheckBox("Show Legend")
        show_legend_cb.setChecked(True)

        graph_color_label = QLabel("Graph Color:")
        graph_color_combo = QComboBox()
        graph_color_combo.addItems(["Blue", "Red", "Green", "Black"])

        graph_settings_layout.addWidget(show_grid_cb)
        graph_settings_layout.addWidget(show_legend_cb)
        graph_settings_layout.addWidget(graph_color_label)
        graph_settings_layout.addWidget(graph_color_combo)
        graph_settings_tab.setLayout(graph_settings_layout)

        settings_toolbox.addItem(graph_settings_tab, "Graph Settings")

        # Emit signal when the tab changes
        settings_toolbox.currentChanged.connect(self.tabChanged.emit)

        # Set up the layout for the settings toolbox
        settings_v_box = QVBoxLayout()
        settings_v_box.addWidget(settings_toolbox, 0, Qt.AlignmentFlag.AlignTop)

        return settings_v_box
    
    def addresultsLayout(self): 
        self.results_label = QLabel("results Layout")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_layout.addWidget(self.results_label)
    
    def plotV1Graph(self, value):
        self.Xm[:-1] = self.Xm[1:]                      # shift data in the temporal mean 1 sample left
        self.Xm[-1] = float(value)                      # vector containing the instantaneous values
        self.ptr += 1                                   # update x position for displaying the curve
        self.curve1.setData(self.Xm)                    # set the curve with this data
        self.curve1.setPos(self.ptr, 0)                 # set x position in the graph to 0
        QtWidgets.QApplication.processEvents()          # you MUST process the plot now
    
    def plotV2Graph(self, value):
        self.Xm2[:-1] = self.Xm2[1:]                      # shift data in the temporal mean 1 sample left
        self.Xm2[-1] = float(value)                      # vector containing the instantaneous values
        self.ptr += 1                                   # update x position for displaying the curve
        self.curve1.setData(self.Xm2)                    # set the curve with this data
        self.curve1.setPos(self.ptr, 0)                 # set x position in the graph to 0
        QtWidgets.QApplication.processEvents()          # you MUST process the plot now

    def plotTTGraph(self, value):
        self.Xm3[:-1] = self.Xm3[1:]                      # shift data in the temporal mean 1 sample left
        self.Xm3[-1] = float(value)                      # vector containing the instantaneous values
        self.ptr += 1                                   # update x position for displaying the curve
        self.curve1.setData(self.Xm3)                    # set the curve with this data
        self.curve1.setPos(self.ptr, 0)                 # set x position in the graph to 0
        QtWidgets.QApplication.processEvents()          # you MUST process the plot now

    def detectCOMPort(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if 'USB-SERIAL CH340' in port.description:
                com_port = port.device
                break
        else:
            raise Exception("USB-SERIAL CH340 not found")
        return com_port

    def openCANBus(self):
        database = cantools.db.load_file("CAN/DANCANSERVER/VESC.dbc")
        com_port = self.detectCOMPort()
        can_bus = can.interface.Bus(interface='seeedstudio',
                                    channel=com_port,
                                    baudrate=2000000,
                                    bitrate=500000)
        tester = cantools.tester.Tester('VESC1', database, can_bus)
        tester.start()
        self.can_bus = can_bus  # Store the CAN bus instance
        return tester

    def closeCANBus(self):
        try:
            if hasattr(self, 'can_bus') and self.can_bus is not None:
                self.can_bus.shutdown()
        except Exception as e:
            print(f"Error during CAN bus shutdown")
    
    @pyqtSlot()
    def startThread(self):
        self._thread.start()
        key = 'Status_RPM_V2'  # example key
        windowWidth = self.windowWidth  # example window width
        version = 2  # example version
        tester = self.openCANBus()  # example tester object
        self.requestData.emit(tester, key, version, windowWidth)

    @pyqtSlot()
    def stopThread(self):
        self._threaded._running = False
        self._thread.quit()
        self._thread.wait()
        self.closeCANBus()  # Close the CAN bus connection

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = Window()
    window.show()
    sys.exit(app.exec())