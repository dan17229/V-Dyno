from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QToolBox,
    QVBoxLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
)


class ToolsPanel(QVBoxLayout):
    """A class to set up a permanent tools panel with a QToolBox for motor control, graph settings, and data filters."""

    def __init__(self, parent: QWidget):
        super().__init__()
        self.parent = parent
        self.setupToolsPanel()

    def setupToolsPanel(self):
        """Set up a permanent tools panel with a QToolBox for motor control, graph settings, and data filters."""
        settings_toolbox = QToolBox()
        settings_toolbox.setFixedWidth(300)
        settings_toolbox.setCurrentIndex(0)  # Show the first tab by default

        # Tab 1: Motor Control
        motor_control_tab = QWidget()
        motor_control_layout = QVBoxLayout()
        motor_control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        MUT_current_label = QLabel("Motor 1 RPM:")
        MUT_current_box = QSpinBox()
        MUT_current_box.setRange(0, 1000)  # Set the range for RPM input
        MUT_current_box.setSingleStep(10)  # Set the step size for duty cycle input
        MUT_current_box.setValue(0)  # Set a default value

        load_rpm_label = QLabel("Motor 2 brake current:")
        load_rpm_input = QDoubleSpinBox()
        load_rpm_input.setRange(-5.0, 5.0)  # Set the range for duty cycle input
        load_rpm_input.setSingleStep(0.1)  # Set the step size for duty cycle input
        load_rpm_input.setValue(0)  # Set a default value

        # Connect the valueChanged signal to the parent's change_Load_Speed method
        load_rpm_input.valueChanged.connect(self.parent.change_load_current)

        motor_control_layout.addWidget(MUT_current_label)
        motor_control_layout.addWidget(MUT_current_box)
        motor_control_layout.addWidget(load_rpm_label)
        motor_control_layout.addWidget(load_rpm_input)

        motor_control_tab.setLayout(motor_control_layout)
        settings_toolbox.addItem(motor_control_tab, "Motor Control")

        # Tab 2: Graph Settings
        graph_settings_tab = QWidget()
        graph_settings_layout = QVBoxLayout()
        graph_settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        show_grid_cb = QCheckBox("Show Grid")
        show_grid_cb.setChecked(True)

        show_legend_cb = QCheckBox("Show Legend")
        show_legend_cb.setChecked(True)

        graph_color_label = QLabel("Graph Color:")
        graph_color_combo = QComboBox()
        graph_color_combo.addItems(["Blue", "Red", "Green", "Black"])

        graph_settings_layout.addWidget(show_grid_cb)
        graph_settings_layout.addWidget(show_legend_cb)
        graph_settings_layout.addWidget(graph_color_label)
        graph_settings_layout.addWidget(graph_color_combo)
        graph_settings_tab.setLayout(graph_settings_layout)

        settings_toolbox.addItem(graph_settings_tab, "Graph Settings")

        # Emit signal when the tab changes
        settings_toolbox.currentChanged.connect(self.parent.tab_changed)

        # Set up the layout for the settings toolbox
        self.addWidget(settings_toolbox, 0, Qt.AlignmentFlag.AlignTop)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import (
        QApplication,
        QMainWindow,
        QVBoxLayout,
        QToolBox,
        QSpinBox,
        QDoubleSpinBox,
        QLabel,
        QCheckBox,
        QComboBox,
        QWidget,
    )
    from style_sheet import StyleSheet
    from PyQt6.QtCore import pyqtSignal

    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    app.setStyleSheet(StyleSheet)
    class window(QMainWindow):
        tab_changed = pyqtSignal(
            int
        )  # Setup the signal to notify when a tab is changed in UI for later use

        def __init__(self):
            super().__init__()
            self.show

    trial = window()

    tools_panel = ToolsPanel(trial)

    # Create a central widget and set the layout
    central_widget = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    main_layout.addLayout(tools_panel)
    central_widget.setLayout(main_layout)

    trial.setCentralWidget(central_widget)
    trial.setWindowTitle("Tools Panel")
    trial.show()

    sys.exit(app.exec())
