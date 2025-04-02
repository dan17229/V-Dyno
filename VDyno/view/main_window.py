"""
This file does it all at the minute
author Daniel Muir <danielmuir167@gmail.com>
"""

###### Import the required libraries

import sys
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QThread, QObject
from PyQt6.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton
from pyqtgraph.Qt import QtGui
from style_sheet import StyleSheet
import ctypes
from typing import Protocol
class Presenter(Protocol):
    def openCANBus(self) -> None: ...
    def closeCANBus(self) -> None: ...

###### Make the taskbar icon work (on Windows)


class livePlotThread(QObject):
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
            status_V1 = tester.expect(
                "VESC_Status1_V1", None, timeout=0.01, discard_other_messages=True
            )
            status_V2 = tester.expect(
                "VESC_Status1_V1", None, timeout=0.01, discard_other_messages=True
            )
            status_TT = tester.expect(
                "TEENSY_Status", None, timeout=0.01, discard_other_messages=True
            )
            if status_V1 is not None:
                self.V1_status.emit(status_V1)
            if status_V2 is not None:
                self.V2_status.emit(status_V2)
            if status_TT is not None:
                self.TT_status.emit(status_TT)
            QThread.msleep(10)  # sleep for a short duration to prevent high CPU usage

class Window(QMainWindow):
    """Main window for the VESCdyno GUI."""

    requestData = pyqtSignal(
        object, str, int, int
    )  # Setup the signal to initialise CAN data capture for later use

    tabChanged = pyqtSignal(
        int
    )  # Setup the signal to notify when a tab is changed in UI for later use

    def __init__(self):  # **kwargs could be useful, but not implemented
        super().__init__()

        # Create a thread to run the CAN bus capture
        self._thread = QThread()
        self._threaded = CANCapture()
        self.requestData.connect(self._threaded.startReceiving)
        self._thread.started.connect(self._threaded.startThread)
        self._threaded.moveToThread(self._thread)

        self.initializeUI()
        self.setupMenu()

        # Connect the aboutToQuit signal to the stopThread method
        QApplication.instance().aboutToQuit.connect(self.stopThread)

    def initializeUI(self):
        """Initialize the window and display its contents."""
        myappid = "V-dyno"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        app.setStyle("WindowsVista")  # Replace 'Windows' with the desired style
        app.setWindowIcon(QtGui.QIcon("GUI/images/icon.svg"))
        self.showMaximized()
        self.setMinimumSize(800, 700)
        self.setWindowTitle("VESCdyno")
        self.setupWindow()
        self.show()

    def setupWindow(self):
        # Create the tools panel
        tools_panel = ToolsPanel(Window)

        # Create Live Plot panel
        self.live_plot = LivePlots(Window)

        # Create Animation Window
        self.anim_dock = AnimWindow(Window)
        #addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.anim_dock)

        # Create Start Button
        button_layout = self.setupStartButton()
        self.button_widget = QWidget()
        self.button_widget.setLayout(button_layout)

        # Create a layout for the main window
        self.main_layout = (
            QHBoxLayout()
        )  # Use horizontal layout to place tools panel on the left
        
        self.graph_layout = QVBoxLayout()  # Vertical layout for the graph and buttons

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
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction(self.toggle_animation_act)

    def addresultsLayout(self):
        self.results_label = QLabel("results Layout")
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_layout.addWidget(self.results_label)

    @pyqtSlot()
    def startThread(self):
        self._thread.start()
        key = "Status_RPM_V1"  # example key
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
    app.setStyleSheet(StyleSheet)
    window = Window()
    window.show()
    sys.exit(app.exec())
