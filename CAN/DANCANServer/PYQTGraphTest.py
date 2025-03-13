# Import libraries
from numpy import linspace
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import serial
import can
import cantools
import os
import serial.tools.list_ports

os.chdir(os.path.dirname(os.path.abspath(__file__)))
ports = list(serial.tools.list_ports.comports())
for port in ports:
    if 'USB-SERIAL CH340' in port.description:
        com_port = port.device
        break
else:
    raise Exception("USB-SERIAL CH340 not found")

### START QtApp #####
app = QtWidgets.QApplication([])            # you MUST do this once (initialize things)
####################

win = pg.GraphicsLayoutWidget(show=True, title="Dyno Realtime") # creates a window

# First plot
p1 = win.addPlot(title="M.U.T Current")  # creates empty space for the first plot in the window
curve1 = p1.plot()                         # create an empty "plot" (a curve to plot)

# Second plot
win.nextRow()                              # move to the next row in the layout
p2 = win.addPlot(title="Generator Current")  # creates empty space for the second plot in the window
curve2 = p2.plot()                         # create an empty "plot" (a curve to plot)

windowWidth = 500                          # width of the window displaying the curve
Xm1 = linspace(0, 0, windowWidth)          # create array that will contain the relevant time series for plot 1
Xm2 = linspace(0, 0, windowWidth)          # create array that will contain the relevant time series for plot 2
ptr = -windowWidth                         # set first x position

can_bus = can.interface.Bus(interface='seeedstudio',
                            channel=com_port,
                            baudrate=2000000,
                            bitrate=500000)

database = cantools.db.load_file("VESC.dbc")
tester = cantools.tester.Tester('VESC1',
                                database,
                                can_bus)
tester.start()

# Realtime data plot. Each time this function is called, the data display is updated
def update():
    global ptr, Xm1, Xm2
    tester.send('VESC_Command_RPM_V1', {'Command_RPM_V1': 1500})
    status1 = tester.expect('VESC_Status1_V1', None, timeout=.01, discard_other_messages=True)
    status2 = tester.expect('VESC_Status1_V2', None, timeout=.01, discard_other_messages=True)
    #print(status2)
    if status1 is not None:
        plotGraph(curve1, Xm1, status1, 'Status_TotalCurrent_V1')
    if status2 is not None:
        plotGraph(curve2, Xm2, status2, 'Status_TotalCurrent_V2')

def plotGraph(curve, Xm, status, key):
    global ptr
    status[key] /= 10
    Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
    value = status[key]                   # read line (single value) from the serial port
    Xm[-1] = float(value)                 # vector containing the instantaneous values      
    ptr += 1                              # update x position for displaying the curve
    curve.setData(Xm)                     # set the curve with this data
    curve.setPos(ptr, 0)                  # set x position in the graph to 0
    QtWidgets.QApplication.processEvents() # you MUST process the plot now

class KeyPressHandler(QtCore.QObject):
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Up:
                tester.send('VESC_Command_DutyCycle_V2', {'Command_DutyCycle_V2': 0.2})
                return True
        return super().eventFilter(obj, event)

keyPressHandler = KeyPressHandler()
app.installEventFilter(keyPressHandler)

### MAIN PROGRAM #####    
# this is a brutal infinite loop calling your realtime data plot
while True: update()

### END QtApp ####
pg.QtWidgets.QApplication.exec_() # you MUST put this at the end
##################