"""
This file contains the animation window widget.
"""

from PyQt6.QtGui import QPixmap

class AnimWindow():

    def setAnimWindow(self):
        """Set animation window"""
        anim_dock = QDockWidget()
        anim_dock.setWindowTitle("Setup Diagram")

        anim_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # Allow closing
        anim_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)

        # Load the image into a QLabel
        image_label = QLabel()
        pixmap = QPixmap("images/setup.png")
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
        anim_dock.setWidget(window_container)

        # Set a fixed height for the dock widget
        anim_dock.setMinimumHeight(150)  # Adjust the height as needed
        anim_dock.setMaximumHeight(400)  # Adjust the height as needed

        return anim_dock
    
if __name__ == "__main__":
    from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel, QApplication, QMainWindow
    from PyQt6.QtCore import Qt
    import sys
    import os
    os.chdir("VDyno")

    app = QApplication(sys.argv)
    app.setStyle('WindowsVista')

    window = QMainWindow()

    anim = AnimWindow()
    anim_widget = anim.setAnimWindow()

    # Create a central widget and set the layout
    central_widget = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    main_layout.addWidget(anim_widget)
    central_widget.setLayout(main_layout)

    window.setCentralWidget(central_widget)
    window.setWindowTitle("Anim Window")
    window.show()

    sys.exit(app.exec())