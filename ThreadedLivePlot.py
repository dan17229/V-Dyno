from itertools import count, islice
import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from numpy import linspace
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import serial
import can
import cantools
import os
import serial.tools.list_ports
from GUI.Styles.StyleSheet import style_sheet

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
            status = tester.expect(status_key, None, timeout=.01, discard_other_messages=True)
            if status is not None:
                value = status[key]  # read line (single value) from the serial por
                self.result.emit(value)
            QtCore.QThread.msleep(10)  # sleep for a short duration to prevent high CPU usage

class Window(QMainWindow):
    requestData = pyqtSignal(object, str, int, int)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self._thread = QThread()
        self._threaded = CANCapture()
        self._threaded.result.connect(self.plotGraph)
        self.requestData.connect(self._threaded.startReceiving)
        self._thread.started.connect(self._threaded.startThread)
        self._threaded.moveToThread(self._thread)
        self.initializeUI()
        self.win, self.windowWidth = self.setupWindow()

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
        input_layout = QtWidgets.QVBoxLayout()
        input_widget = QtWidgets.QWidget()
        input_widget.setLayout(input_layout)

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

        input_layout.addWidget(rpm_label)
        input_layout.addWidget(rpm_input)
        input_layout.addWidget(brake_current_label)
        input_layout.addWidget(brake_current_input)

        # Create a proxy widget to embed the QWidget into the GraphicsLayoutWidget
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(input_widget)

        # Create an instance of GraphicsLayoutWidget
        win = pg.GraphicsLayoutWidget()

        # Apply the stylesheet to the GraphicsLayoutWidget
        win.setStyleSheet(style_sheet)

        # Add the proxy widget to the GraphicsLayoutWidget
        win.addItem(proxy, row=0, col=0)

        # First plot
        self.p1 = win.addPlot(title="M.U.T RPM", row=0, col=1)  # creates empty space for the first plot in the window
        self.curve1 = self.p1.plot()  # create an empty "plot" (a curve to plot)
        print("Plot initialized")  # Debug print statement

        windowWidth = 500  # width of the window displaying the curve

        self.Xm = linspace(0, 0, windowWidth)  # create array that will contain the relevant time series for plot
        self.ptr = -windowWidth

        return win, windowWidth
    
    @pyqtSlot(object)
    def plotGraph(self, value):
        print(f"plotGraph called with value: {value}")  # Debug print statement
        self.Xm[:-1] = self.Xm[1:]                      # shift data in the temporal mean 1 sample left
        self.Xm[-1] = float(value)                      # vector containing the instantaneous values
        self.ptr += 1                                   # update x position for displaying the curve
        print(f"Updated Xm: {self.Xm}")                 # Debug print statement
        self.curve1.setData(self.Xm)                    # set the curve with this data
        self.curve1.setPos(self.ptr, 0)                 # set x position in the graph to 0
        QtWidgets.QApplication.processEvents()          # you MUST process the plot now
        print(f"Plot updated at position: {self.ptr}")  # Debug print statement

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
        if hasattr(self, 'can_bus') and self.can_bus is not None:
            self.can_bus.shutdown()
    
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