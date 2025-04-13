"""
LivePlots window for plotting realtime data
"""

import pyqtgraph as pg
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QComboBox
from numpy import linspace


class Plot:
    """Class handling creation and updating of plot windows"""

    def __init__(self, windowWidth: int) -> None:
        super().__init__()
        self.Xm = linspace(
            0, 0, windowWidth
        )  # create array that will contain the relevant time series for plot
        self.ptr = -windowWidth  # the position to plot them in

    def setup_dropdown(self, options: list) -> object:
        dropdown = QComboBox()
        dropdown.setFixedWidth(200)
        dropdown.addItems(options)
        dropdown_proxy = QtWidgets.QGraphicsProxyWidget()
        dropdown_proxy.setWidget(dropdown)
        return dropdown_proxy

    def plot_settings(self, plot: object) -> None:
        plot.getAxis("left").setPen(
            pg.mkPen(color="k", width=2)
        )  # Black left axis with increased width
        plot.getAxis("bottom").setPen(
            pg.mkPen(color="k", width=2)
        )  # Black bottom axis with increased width
        self.curve = plot.plot(
            pen=pg.mkPen(color="k", width=2)
        )  # Black line with increased width

    def plot(self, value) -> None:
        self.Xm[:-1] = self.Xm[1:]  # shift data in the temporal mean 1 sample left
        self.Xm[-1] = float(value)  # vector containing the instantaneous values
        self.ptr += 1  # update x position for displaying the curve
        self.curve.setData(self.Xm)  # set the curve with this data
        self.curve.setPos(self.ptr, 0)  # set x position in the graph to 0
        QtWidgets.QApplication.processEvents()  # you MUST process the plot now


class PlotWindow(pg.GraphicsLayoutWidget):
    """Class forming the plot window UI"""

    def __init__(self) -> None:
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        super().__init__()
        self.setupLivePlot()

    def setupLivePlot(self) -> None:
        ## Switch to using white background and black foreground
        # Create an instance of GraphicsLayoutWidget

        windowWidth = 500  # width of the window displaying the curve

        self.MUT_plot = Plot(windowWidth)
        self.Load_plot = Plot(windowWidth)
        self.TT_plot = Plot(windowWidth)

        dropdown1 = self.MUT_plot.setup_dropdown(
            ["MUT Current", "Option 2", "Option 3"]
        )
        dropdown2 = self.Load_plot.setup_dropdown(
            ["Load motor RPM", "Option B", "Option C"]
        )
        dropdown3 = self.TT_plot.setup_dropdown(["Torque Transducer"])

        # adding the plots to the window

        self.addItem(dropdown1, row=0, col=1)
        self.addItem(dropdown2, row=1, col=1)
        self.addItem(dropdown3, row=2, col=1)

        self.p1 = self.addPlot(row=0, col=2)
        self.p2 = self.addPlot(row=1, col=2)
        self.p3 = self.addPlot(row=2, col=2)

        # make the colours right

        self.MUT_plot.plot_settings(self.p1)
        self.Load_plot.plot_settings(self.p2)
        self.TT_plot.plot_settings(self.p3)


if __name__ == "__main__":
    from PyQt6 import QtWidgets
    from PyQt6.QtWidgets import QComboBox
    from numpy import linspace
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    live_plot = PlotWindow()
    live_plot.show()

    import random
    import time

    data1 = 0
    data2 = 0
    data3 = 0

    while True:
        data1 = data1 + random.randint(-10, 10)
        data2 = data2 + random.randint(-10, 10)
        data3 = data3 + random.randint(-10, 10)
        live_plot.MUT_plot.plot(data1)
        live_plot.Load_plot.plot(data2)
        live_plot.TT_plot.plot(data3)
        time.sleep(0.01)

    sys.exit(app.exec())
