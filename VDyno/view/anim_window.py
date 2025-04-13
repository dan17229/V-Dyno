"""
This file contains the animation window widget.
"""

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QApplication,
    QMainWindow,
)
from PyQt6.QtCore import Qt


class AnimWindow(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setAnimWindow()

    def setAnimWindow(self):
        """Set animation window"""
        self.setWindowTitle("Setup Diagram")

        self.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # Allow closing
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)

        # Load the image into a QLabel
        image_label = QLabel()
        pixmap = QPixmap("VDyno/images/setup.png")
        pixmap = pixmap.scaled(
            400,
            400,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        image_label.setPixmap(pixmap)
        image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center the image within the label

        window_layout = QVBoxLayout()
        window_layout.addWidget(image_label)

        # Set the QLabel as the widget for the dock
        window_container = QWidget()
        window_container.setLayout(window_layout)
        self.setWidget(window_container)

        # Set a fixed height for the dock widget
        self.setMinimumHeight(150)  # Adjust the height as needed
        self.setMaximumHeight(400)  # Adjust the height as needed


if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")

    window = QMainWindow()

    anim = AnimWindow()

    # Create a central widget and set the layout
    central_widget = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    main_layout.addWidget(anim)
    central_widget.setLayout(main_layout)

    window.setCentralWidget(central_widget)
    window.setWindowTitle("Anim Window")
    window.show()

    sys.exit(app.exec())
