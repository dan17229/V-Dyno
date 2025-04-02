"""
This module contains the LivePlots class, which is used to create a live plot of the data
"""
import pyqtgraph as pg
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QComboBox
from numpy import linspace
class LivePlots():
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setupLivePlot()

    def setupLivePlot(self):
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        # Create an instance of GraphicsLayoutWidget
        win = pg.GraphicsLayoutWidget()

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
    
if __name__ == "__main__":
    from PyQt6 import QtWidgets
    from PyQt6.QtWidgets import QComboBox
    from numpy import linspace
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle('WindowsVista')
    live_plot = LivePlots(None)
    window = live_plot.setupLivePlot()
    window.show()
    sys.exit(app.exec())