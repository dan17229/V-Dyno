"""
author Daniel Muir <danielmuir167@gmail.com>
"""

# Import the required libraries

import sys
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
    QToolBar,
    QSizePolicy,
    QComboBox,
)
from PyQt6.QtGui import QAction, QIcon
from pyqtgraph.Qt import QtGui
import ctypes
from typing import Protocol
from functools import partial

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
    plot_MUT_changed = pyqtSignal(
        int
    )  # Signal to notify when desired MUTplot is changed
    plot_load_changed = pyqtSignal(int)
    plot_TT_changed = pyqtSignal(int)

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app

    def init_UI(self, presenter: Presenter) -> None:
        """Initialize the window and display its contents."""
        # setup up icon, style, size.
        self.presenter = presenter
        self.setMinimumSize(800, 700)
        self.setWindowTitle("V-Dyno")
        self._create_actions()
        self.setup_window()
        self._setup_menu()
        self._setup_tool_bar()
        self._connect_actions()
        self.show()
        self.presenter.start_plots()
        sys.exit(self.app.exec())

    def setup_window(self):
        """Create the main window and its components."""
        self.tools_panel = ToolsPanel(self)
        self.live_plot = PlotWindow(self.presenter)
        print(type(self.live_plot))
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
            # self.button_widget.show()

        elif index == 1:  # "Graph Settings" tab
            self.anim_dock.show()
            self.results_label.show()

    def _create_actions(self) -> None:
        self.selected_experiment = "VDyno/experiments/experiment.JSON"
        # File actions
        self.start_experiment_action = QAction(
            QIcon("VDyno/images/icon_dark.svg"), "&Open...", self
        )
        self.start_experiment_action.triggered.connect(
            partial(self.presenter.start_experiment, self.selected_experiment)
        )  # Connect to presenter 
        self.start_experiment_action.setShortcut("Ctrl+R")
        self.start_recording_action = QAction(
            QIcon("VDyno/images/icon_dark.svg"), "&Record...", self
        )
        self.start_recording_action.triggered.connect(
            self.presenter.start_record_thread
        )
        self.start_recording_action.setShortcut("Ctrl+Shift+R")

    def _connect_actions(self):
        # Connect Open Recent to dynamically populate it
        self.open_recent_menu.aboutToShow.connect(self.populate_open_recent)

    def open_recent_file(self, filename):
        # Logic for opening a recent file goes here...
        print(f"<b>{filename}</b> opened")

    def _setup_menu(self):
        """Create a simple menu to manage the dock widget."""
        menu_bar = self.menuBar()
        # Create file menu and add actions
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("Open", self.presenter.start_experiment)
        self.open_recent_menu = file_menu.addMenu("Open Recent")
        # Create view menu and add actions
        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.anim_dock.toggleViewAction())

    def populate_open_recent(self):
        # Step 1. Remove the old options from the menu
        self.open_recent_menu.clear()
        # Step 2. Dynamically create the actions
        actions = []
        filenames = [f"File-{n}" for n in range(5)]
        for filename in filenames:
            action = QAction(filename, self)
            action.triggered.connect(partial(self.open_recent_file, filename))
            actions.append(action)
        # Step 3. Add the actions to the menu
        self.open_recent_menu.addActions(actions)

    def separator(self, width: int) -> QWidget:
        separator = QWidget()
        separator.setObjectName(
            "CustomSpacer"
        )  # Set the object name for stylesheet targeting
        separator.setFixedWidth(20)  # Set the desired width of the separator
        return separator

    def _setup_tool_bar(self) -> None:
        ToolBar = QToolBar("Help", self)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, ToolBar)
        ToolBar.setMovable(False)
        ToolBar.iconSize = QSize(20, 20)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        spacer.setObjectName(
            "CustomSpacer"
        )  # Set the object name for stylesheet targeting
        ToolBar.addWidget(spacer)
        ToolBar.addAction(self.start_recording_action)
        ToolBar.addWidget(self.separator(20))
        dropdown = QComboBox()
        dropdown.setFixedWidth(200)
        experiment_list = self.presenter.get_experiment_list()
        dropdown.addItems(experiment_list)
        ToolBar.addWidget(dropdown)
        ToolBar.addWidget(self.separator(20))
        ToolBar.addAction(self.start_experiment_action)
        ToolBar.addWidget(self.separator(20))

    def addresultsLayout(self):
        self.results_label = QLabel("results Layout")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_layout.addWidget(self.results_label)

    def change_MUT_current(self, value):
        self.presenter.desired_MUT_current = value

    def change_load_rpm(self, value):   
        self.presenter.desired_load_rpm = value

def create_UI() -> MainWindow:
    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    myappid = "V-dyno"  # arbitrary string as name
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app.setStyle("WindowsVista")
    app.setWindowIcon(QtGui.QIcon("VDyno/images/icon.svg"))

    # Create the main window
    main_window = MainWindow(app)

    return main_window,app


if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

    class DummyPresenter:
        def plot_MUT_changed(self, value: float) -> None: ...

        def plot_load_changed(self, value: float) -> None: ...

        def plot_TT_changed(self, value: float) -> None: ...

        def start_experiment(self, experiment: str) -> None:
            print(f"Starting {experiment}")

        def get_experiment_list(self) -> list[str]:
            return ["Experiment 1", "Experiment 2", "Experiment 3"]

    view = create_UI()
    view.init_UI(DummyPresenter())
