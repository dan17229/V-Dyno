"""
author Daniel Muir <danielmuir167@gmail.com>
"""

# Import the required libraries

import sys
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
    QPushButton,
)
from pyqtgraph.Qt import QtGui
import ctypes
from typing import Protocol

# Import the other windows to display
if __name__ == "__main__":
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from VDyno.view.style_sheet import StyleSheet
from VDyno.view.anim_window import AnimWindow
from VDyno.view.live_plots import PlotWindow
from VDyno.view.tools_panel import ToolsPanel

class Presenter(Protocol):  # allow for duck-typing of presenter class
    def openCANBus(self) -> None: ...
    def closeCANBus(self) -> None: ...
class MainWindow(QMainWindow):
    """Main window for the VESCdyno GUI."""
    tab_changed = pyqtSignal(int)  # Signal to notify when a tab is changed
    plot_MUT_changed = pyqtSignal(int)  # Signal to notify when desired MUTplot is changed
    plot_load_changed = pyqtSignal(int) 
    plot_TT_changed = pyqtSignal(int) 

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app

    def init_UI(self, presenter: Presenter) -> None:
        """Initialize the window and display its contents."""
        # setup up icon, style, size.
        self.presenter = presenter
        self.showMaximized()
        self.setMinimumSize(800, 700)
        self.setWindowTitle("V-Dyno")
        #self.setup_thread()
        self.setup_window()
        self.setup_menu()
        self.show()
        sys.exit(self.app.exec())

    def setup_window(self):
        """Create the main window and its components."""
        self.tools_panel = ToolsPanel(self)
        self.live_plot = PlotWindow(self.presenter)
        self.anim_dock = AnimWindow()
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.anim_dock)

        # Create Start Button
        # thread_button = self.setup_thread_button()

        # Create a layout for the main window
        self.graph_layout = QVBoxLayout()  # Vertical layout for the graph and buttons

        self.graph_layout.addWidget(self.live_plot)
        self.graph_layout.addWidget(self.anim_dock)
        # self.graph_layout.addWidget(thread_button)

        # Initialize results_label but hide it initially
        self.results_label = QLabel("results Layout")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_label.hide()  # Hide it initially
        self.graph_layout.addWidget(self.results_label)

        # Add the tools panel and graph layout to the main layout
        self.main_layout = (
            QHBoxLayout()
        )  # Use horizontal layout to place tools panel on the left
        self.main_layout.addLayout(self.tools_panel)
        self.main_layout.addLayout(self.graph_layout)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self.tab_changed.connect(self.on_tab_change)

    def on_tab_change(self, index):
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
            #self.button_widget.show()

        elif index == 1:  # "Graph Settings" tab
            self.anim_dock.show()
            self.results_label.show()

    def setup_thread_button(self) -> QWidget:
        # Add start button
        start_button = QPushButton("Start Thread")
        start_button.clicked.connect(self.startThread)

        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.stopThread)
        button_layout = QHBoxLayout()

        button_layout.addWidget(start_button)
        button_layout.addWidget(close_button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        return button_widget

    def setup_menu(self):
        """Create a simple menu to manage the dock widget."""
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        # Create view menu and add actions
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction(self.anim_dock.toggleViewAction())

    def addresultsLayout(self):
        self.results_label = QLabel("results Layout")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_layout.addWidget(self.results_label)

    def update_MUT_plot(self, value: float) -> None:
        """Update the MUT plot with the given value."""
        self.live_plot.MUT_plot.plot(value)
    
    def update_load_motor_plot(self, value: float) -> None:
        """Update the load motor plot with the given value."""
        self.live_plot.Load_plot.plot(value)

    def update_transducer_plot(self, value: float) -> None:
        """Update the torque transducer plot with the given value."""
        self.live_plot.TT_plot.plot(value)

def create_UI() -> MainWindow:
    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    myappid = "V-dyno"  # arbitrary string as name
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app.setStyle("WindowsVista")
    app.setWindowIcon(QtGui.QIcon("VDyno/images/icon.svg"))

    # Create the main window
    main_window = MainWindow(app)

    return main_window

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from VDyno.presenter.dummy_presenter import DummyPresenter
    presenter = DummyPresenter()
    view = create_UI()
    view.init_UI(presenter)