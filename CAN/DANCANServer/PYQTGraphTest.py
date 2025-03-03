# Import libraries
from numpy import *
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import serial
import can
import cantools
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

### START QtApp #####
app = QtWidgets.QApplication([])            # you MUST do this once (initialize things)
####################

win = pg.GraphicsLayoutWidget(show=True, title="Signal from serial port") # creates a window
p = win.addPlot(title="Realtime plot")  # creates empty space for the plot in the window
curve = p.plot()                        # create an empty "plot" (a curve to plot)

windowWidth = 500                       # width of the window displaying the curve
Xm = linspace(0,0,windowWidth)          # create array that will contain the relevant time series     
ptr = -windowWidth                      # set first x position

can_bus = can.interface.Bus(interface='seeedstudio',
                            channel='COM4',
                            baudrate=2000000,
                            bitrate=500000)

database = cantools.db.load_file("VESC.dbc")
tester = cantools.tester.Tester('VESC1',
                                database,
                                can_bus)
tester.start()

# Realtime data plot. Each time this function is called, the data display is updated
def update():
    global curve, ptr, Xm
    tester.send('VESC_Command_RPM_V1', {'Command_RPM_V1': 1500})
    tester.send('VESC_Command_AbsHBrakeCurrent_V2', {'Command_HBrakeCurrent_V2': 1})
    status = tester.expect('VESC_Status1_V1', None, timeout=.1, discard_other_messages=True)
    status2 = tester.expect('VESC_Status1_V2', None, timeout=.1, discard_other_messages=True)
    Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
    value = status2[2]                    # read line (single value) from the serial port
    Xm[-1] = float(value)                 # vector containing the instantaneous values      
    ptr += 1                              # update x position for displaying the curve
    curve.setData(Xm)                     # set the curve with this data
    curve.setPos(ptr,0)                   # set x position in the graph to 0
    QtWidgets.QApplication.processEvents()    # you MUST process the plot now

### MAIN PROGRAM #####    
# this is a brutal infinite loop calling your realtime data plot
while True: update()

### END QtApp ####
pg.QtWidgets.QApplication.exec_() # you MUST put this at the end
##################