"""
LivePlots window for plotting realtime data
"""

import pyqtgraph as pg
from PyQt6.QtWidgets import QComboBox
from numpy import zeros
from typing import Protocol

class Presenter(Protocol):  # allow for duck-typing of presenter class
    def plot_MUT_changed(self, index: int) -> None: ...
    def plot_load_changed(self, index: int) -> None: ...
    def plot_TT_changed(self, index: int) -> None: ...

def setup_dropdown(options: list) -> object:
    dropdown = QComboBox()
    dropdown.setFixedWidth(200)
    dropdown.addItems(options)
    return dropdown

    
class Plot_Data():
    """Class handling creation and updating of plot windows"""
    def __init__(self, window_width = 200) -> None:
        super().__init__()
        self.Xm = zeros(window_width)  # Array to hold the data for the plot

    def extend(self, value) -> None:
        self.Xm[:-1] = self.Xm[1:]  # Shift data in the temporal mean 1 sample left
        self.Xm[-1] = float(value)  # Add the new value to the end of the array
        return self.Xm  # Return the updated array for plotting

class PlotWindow(pg.LayoutWidget):
    """Class forming the plot window UI"""

    def __init__(self, parent: Presenter) -> None:
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        super().__init__()
        self.parent = parent
        self.setMinimumHeight(400)
        self.MUT_index = 0
        self.Load_index = 0
        self.TT_index = 0
        self.setupInputs()
        self.setupLivePlot()
        self.show()

    def MUT_index_changed(self, index: int) -> None:
        self.MUT_index=index

    def Load_index_changed(self, index: int) -> None:
        self.Load_index=index

    def TT_index_changed(self, index: int) -> None:
        self.TT_index=index

    def setupInputs(self) -> None:
        dropdown1 = setup_dropdown(["MUT RPM", "MUT current", "MUT duty cycle"])
        dropdown2 = setup_dropdown(["Load motor RPM", "Load current", "Load duty cycle"])
        dropdown3 = setup_dropdown(["Torque Transducer"])

        dropdown1.currentIndexChanged.connect(self.MUT_index_changed)
        dropdown2.currentIndexChanged.connect(self.Load_index_changed)
        dropdown3.currentIndexChanged.connect(self.TT_index_changed)

        # adding the plots to the window)
        self.addWidget(dropdown1, row=0, col=0)
        self.addWidget(dropdown2, row=1, col=0)
        self.addWidget(dropdown3, row=2, col=0)

    def setupLivePlot(self) -> None:
        view = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()
        view.pg.setConfigOptions(antialias=True)  # Enable antialiasing for smoother plots
        self.parent.app.aboutToQuit.connect(view.close)

        # view = pg.GraphicsLayoutWidget()  # Use GraphicsLayoutWidget for local plots
        # self.MUT_plot = view.addPlot(row=0, col=0, title="MUT Plot")
        # self.Load_plot = view.addPlot(row=1, col=0, title="Load Plot")
        # self.TT_plot = view.addPlot(row=2, col=0, title="Torque Transducer Plot")

        # Add the view to the layout
        self.addWidget(view)

        self.addWidget(view, row=0, col=1, rowspan=3)

        # # Create a GraphicsLayout in the remote process
        layout = view.pg.GraphicsLayout()
        view.setCentralItem(layout)

        # # Create PlotItems directly in the remote process
        self.MUT_plot = layout.addPlot(row=0, col=0)
        self.Load_plot = layout.addPlot(row=1, col=0)
        self.TT_plot = layout.addPlot(row=2, col=0)

        # Initialize data arrays for each plot
        self.MUT_data_rpm = Plot_Data()
        self.MUT_data_current = Plot_Data()
        self.MUT_data_duty_cycle = Plot_Data()
        self.Load_data_rpm = Plot_Data()
        self.Load_data_current = Plot_Data()
        self.Load_data_duty_cycle = Plot_Data()
        self.TT_torque = Plot_Data()
    
    def update(self):
        self.MUT_data_rpm.extend(self.parent.dyno.MUT.status["Status_RPM_V1"])
        self.MUT_data_current.extend(self.parent.dyno.MUT.status["Status_TotalCurrent_V1"])
        self.MUT_data_duty_cycle.extend(self.parent.dyno.MUT.status["Status_DutyCycle_V1"])
        
        if self.MUT_index == 0:  # MUT RPM
            self.MUT_plot.plot(self.MUT_data_rpm.Xm, clear=True, _callSync='off', pen='k')
        elif self.MUT_index == 1:  # MUT current
            self.MUT_plot.plot(self.MUT_data_current.Xm, clear=True, _callSync='off', pen='k')
        elif self.MUT_index == 2:  # MUT duty cyclea
            self.MUT_plot.plot(self.MUT_data_duty_cycle.Xm, clear=True, _callSync='off', pen='k')

        self.Load_data_rpm.extend(self.parent.dyno.load_motor.status["Status_RPM_V2"])
        self.Load_data_current.extend(self.parent.dyno.load_motor.status["Status_TotalCurrent_V2"])
        self.Load_data_duty_cycle.extend(self.parent.dyno.load_motor.status["Status_DutyCycle_V2"])
        if self.Load_index == 0:  # Load RPM
            self.Load_plot.plot(self.Load_data_rpm.Xm, clear=True, _callSync='off', pen='k')
        elif self.Load_index == 1:
            self.Load_plot.plot(self.Load_data_current.Xm, clear=True, _callSync='off', pen='k')
        elif self.Load_index == 2:
            self.Load_plot.plot(self.Load_data_duty_cycle.Xm, clear=True, _callSync='off', pen='k')

        self.TT_torque.extend(self.parent.dyno.torque_transducer.status["TorqueValue"])
        self.TT_plot.plot(self.TT_torque.Xm, clear=True, _callSync='off', pen='k')


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    import os
    from random import randint

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

    class DummyPresenter:
        def __init__(self) -> None:
            self.MUT_speed = 0
            self.MUT_brake_current = 0
            self.MUT_duty_cycle = 0
            self.load_speed = 0
            self.load_brake_current = 0
            self.load_duty_cycle = 0
            self.transducer_torque = 0
            self.MUT_status = {"Status_RPM_V1": self.MUT_speed, "Status_TotalCurrent_V1": self.MUT_brake_current, "Status_DutyCycle_V1": self.MUT_duty_cycle}
            self.load_status = {"Status_RPM_V2": self.load_speed, "Status_TotalCurrent_V2": self.load_brake_current, "Status_DutyCycle_V2": self.load_duty_cycle}
            self.TT_status =  {"TorqueValue": self.transducer_torque}
            self.app = QApplication(sys.argv)
            self.app.setStyle("WindowsVista")
        
        def randomise(self):
            for key in self.MUT_status:
                self.MUT_status[key] += randint(-1, 1)
            for key in self.load_status:
                self.load_status[key] += randint(-1, 1)
            for key in self.TT_status:
                self.TT_status[key] += randint(-1, 1)
        
        def plot_MUT_changed(self): ...
        def plot_load_changed(self): ...
        def plot_TT_changed(self): ...

        def run(self):
            sys.exit(self.app.exec())

    example = DummyPresenter()
    live_plot = PlotWindow(example)

    def update():
        live_plot.update()
        example.randomise()

    # Use a QTimer to periodically update the plots
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(10)  # Update every 10 ms

    example.run()
