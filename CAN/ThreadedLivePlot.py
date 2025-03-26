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
    result = pyqtSignal(object)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    @pyqtSlot()
    def startThread(self):
        print("Thread started")

    @pyqtSlot(object, str, int, int)
    def startReceiving(self, tester, key, version, windowWidth):
        self._running = True
        print("Receiving started")
        status_key = f'VESC_Status1_V{version}'
        while self._running:
            tester.flush_input()
            status = tester.expect(status_key, None, timeout=.01, discard_other_messages=True)
            if status is not None:
                value = status[key]  # read line (single value) from the serial por
                self.result.emit(value)
            QtCore.QThread.msleep(10)  # sleep for a short duration to prevent high CPU usage

class Window(QMainWindow):
    requestData = pyqtSignal(object, str, int, int)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        # Make it light theme
        app.setStyle('WindowsVista')  # Replace 'Windows' with the desired style
        app.setWindowIcon(QtGui.QIcon('GUI/icon.svg'))
        self._thread = QThread()
        self._threaded = CANCapture()
        self._threaded.result.connect(self.plotGraph)
        self.requestData.connect(self._threaded.startReceiving)
        self._thread.started.connect(self._threaded.startThread)
        self._threaded.moveToThread(self._thread)
        self.initializeUI()
        self.setupToolsDockWidget()
        self.setupMenu()

        # Connect the aboutToQuit signal to the stopThread method
        QApplication.instance().aboutToQuit.connect(self.stopThread)

    def initializeUI(self):
        """Initialize the window and display its contents."""
        self.showMaximized()
        self.setMinimumSize(1000, 800)
        self.setWindowTitle('VESCdyno')

        self.win, self.windowWidth = self.setupWindow()  # Ensure self.win is initialized here

        # Add start button
        self.start_button = QPushButton("Start Thread")
        self.start_button.clicked.connect(self.startThread)

        # Add close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.stopThread)

        # Create a layout for the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.win)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.show()

    def setupWindow(self):
        # Create an instance of GraphicsLayoutWidget
        win = pg.GraphicsLayoutWidget()

        # Apply the stylesheet to the GraphicsLayoutWidget
        win.setStyleSheet(style_sheet)

        # First plot
        self.p1 = win.addPlot(title="M.U.T RPM", row=0, col=1)  # creates empty space for the first plot in the window
        self.curve1 = self.p1.plot()  # create an empty "plot" (a curve to plot)
        
        windowWidth = 500  # width of the window displaying the curve

        self.Xm = linspace(0, 0, windowWidth)  # create array that will contain the relevant time series for plot
        self.ptr = -windowWidth

        return win, windowWidth
    
    def setupMenu(self):
        """Create a simple menu to manage the dock widget."""
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        # Create view menu and add actions
        view_menu = menu_bar.addMenu('View')
        view_menu.addAction(self.toggle_dock_tools_act)
    
    def setupToolsDockWidget(self):
        """Set up the dock widget that displays different tools and themes for 
        interacting with the chart. Also displays the data values in a table view object."""
        tools_dock = QDockWidget()
        tools_dock.setWindowTitle("Tools")
        tools_dock.setMinimumWidth(400)
        tools_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        # Widgets 

        rpm_label = QtWidgets.QLabel("Motor 1 RPM:")
        rpm_input = QtWidgets.QSpinBox()
        rpm_input.setRange(0, 1000)  # Set the range for RPM input
        rpm_input.setSingleStep(10)  # Set the step size for duty cycle input
        rpm_input.setValue(0)  # Set a default value

        brake_current_label = QtWidgets.QLabel("Motor 2 brake current:")
        brake_current_input = QtWidgets.QDoubleSpinBox()
        brake_current_input.setRange(-5.0, 5.0)  # Set the range for duty cycle input
        brake_current_input.setSingleStep(0.1)  # Set the step size for duty cycle input
        brake_current_input.setValue(0)  # Set a default value

        dock_form = QFormLayout()
        dock_form.setAlignment(Qt.AlignmentFlag.AlignTop)
        dock_form.addRow("RPM:", rpm_input)
        dock_form.addRow("Brake current:", brake_current_input)

        # Create QWidget object to act as a container for dock widgets
        tools_container = QWidget()
        tools_container.setLayout(dock_form)
        tools_dock.setWidget(tools_container)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tools_dock)
        # Handles the visibility of the dock widget
        self.toggle_dock_tools_act = tools_dock.toggleViewAction()
    
    def plotGraph(self, value):
        self.Xm[:-1] = self.Xm[1:]                      # shift data in the temporal mean 1 sample left
        self.Xm[-1] = float(value)                      # vector containing the instantaneous values
        self.ptr += 1                                   # update x position for displaying the curve
        self.curve1.setData(self.Xm)                    # set the curve with this data
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