
# Import necessary modules
import sys, csv
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
    QSlider, QComboBox, QPushButton, QCheckBox, QToolBox, QDockWidget, QHBoxLayout, QVBoxLayout, QAction)
from PyQt5.QtDataVisualization import (Q3DBars, QBarDataItem, QBar3DSeries, 
    QValue3DAxis, QAbstract3DSeries, QAbstract3DGraph, Q3DCamera, Q3DTheme)
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from GUI.Styles.StyleSheet import style_sheet


import os

# Change the current working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class GraphModifier(QObject):
    # Create pyqtSignals for keeping track of the state of the background 
    # and grid when the theme is changed
    background_selected = pyqtSignal(bool)
    grid_selected = pyqtSignal(bool)
    
    def __init__(self, parent, bar_graph):
        super().__init__()
        self.graph = bar_graph
        self.parent = parent

        # Set up rotation and visual variables
        self.horizontal_rotation = 0
        self.vertical_rotation = 0    
        self.camera_preset = Q3DCamera.CameraPresetFront
        self.bar_style = QAbstract3DSeries.MeshBar
        self.bars_are_smooth = False

    def rotateHorizontal(self, rotation):
        self.graph.scene().activeCamera().setCameraPosition(
            rotation, self.vertical_rotation)

    def rotateVertical(self, rotation):
        self.graph.scene().activeCamera().setCameraPosition(
            self.horizontal_rotation, rotation)

    def changeCameraView(self):
        """Change the camera's preset (the angle from which we view the camera) by 
        cycling through Qt's different preset camera views."""
        self.graph.scene().activeCamera().setCameraPreset(self.camera_preset + 1)
        preset = int(self.camera_preset) + 1

        if preset > Q3DCamera.CameraPresetDirectlyBelow:
            # Reset predefined position for camera to 0 (CameraPresetFrontLow)
            self.camera_preset = Q3DCamera.CameraPresetFrontLow
        else: 
            self.camera_preset = Q3DCamera.CameraPreset(preset)
        
    def showOrHideBackground(self, state):
        self.graph.activeTheme().setBackgroundEnabled(state)

    def showOrHideGrid(self, state):
        self.graph.activeTheme().setGridEnabled(state)

    def smoothenBars(self, state):
        """Smoothen the edges of the items in all series."""
        self.bars_are_smooth = state
        for series in self.graph.seriesList():
            series.setMeshSmooth(self.bars_are_smooth)

    def changeTheme(self, theme):
        """Change the theme and appearance of the graph. Update the QCheckbox widgets."""
        active_theme = self.graph.activeTheme()
        active_theme.setType(Q3DTheme.Theme(theme))
        self.background_selected.emit(active_theme.isBackgroundEnabled())
        self.grid_selected.emit(active_theme.isGridEnabled())

    def changeBarStyle(self, style):
        """Change the visual style of the bars."""
        combo_box = self.sender()
        if isinstance(combo_box, QComboBox):
            self.bar_style = QAbstract3DSeries.Mesh(combo_box.itemData(style))
            for series in self.graph.seriesList():
                series.setMesh(self.bar_style)

    def showOrHideSeries(self, state):
        """Show or hide the secondary series. seriesList()[1] refers to Spokane; 
        seriesList()[2] refers to Richmond."""
        checkbox = self.sender()
        if state == Qt.Checked and checkbox.text() == "Show Second Series":
            self.graph.seriesList()[1].setVisible(True)
        elif state != Qt.Checked and checkbox.text() == "Show Second Series":
            self.graph.seriesList()[1].setVisible(False)

        if state == Qt.Checked and checkbox.text() == "Show Third Series":
            self.graph.seriesList()[2].setVisible(True)
        elif state != Qt.Checked and checkbox.text() == "Show Third Series":
            self.graph.seriesList()[2].setVisible(False)
        
    def changeSelectionStyle(self, style):
        """Choose the style used to select data, by rows, columns or other options."""
        combo_box = self.sender()
        if isinstance(combo_box, QComboBox):
            selection_style = combo_box.itemData(style)
            self.graph.setSelectionMode(QAbstract3DGraph.SelectionFlags(selection_style))
    
    def selectYears(self, year):
        """Select a specific year to view."""
        if year >= len(self.parent.years):
            self.graph.axes()[1].setRange(0, len(self.parent.years) - 1)
        else:
            self.graph.axes()[1].setRange(year, year)

    def selectMonths(self, month):
        """Select a specific month to view."""
        if month >= len(self.parent.months):
            self.graph.axes()[0].setRange(0, len(self.parent.months) - 1)
        else:
            self.graph.axes()[0].setRange(month, month)

class SimpleBarGraph(QMainWindow):

    def __init__(self):
        super().__init__() 
        self.initializeUI() 

    def setupMenu(self):
        """Set up menu bar."""
        # Create actions for file menu
        save_act = QAction('Save', self)
        save_act.setShortcut('Ctrl+S')
        #save_act.triggered.connect(self.saveTableToFile)

        exit_act = QAction('Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.triggered.connect(self.close)

        # Create menubar
        menu_bar = self.menuBar()
        # For MacOS users, places menu bar in main window
        menu_bar.setNativeMenuBar(False)

        # Create file menu and add actions
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(save_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)
        view_menu = menu_bar.addMenu('View')
        view_menu.addAction(self.toggle_dock_tools_act)

    def setupToolsDockWidget(self):
        """Set up the dock widget that displays different tools and themes for 
        interacting with the chart. Also displays the data values in a table view object."""
        tools_dock = QDockWidget()
        tools_dock.setWindowTitle("Tools")
        tools_dock.setMinimumWidth(400)
        tools_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Create widgets for dock widget area
        themes_cb = QComboBox()
        themes_cb.addItems(["Light", "Cerulean Blue", "Dark", "Sand Brown", 
            "NCS Blue", "High Contrast", "Icy Blue", "Qt"])
        themes_cb.currentTextChanged.connect(self.changeChartTheme)

        self.animations_cb = QComboBox()
        self.animations_cb.addItem("No Animation", QChart.NoAnimation)
        self.animations_cb.addItem("Grid Animation", QChart.GridAxisAnimations)
        self.animations_cb.addItem("Series Animation", QChart.SeriesAnimations)
        self.animations_cb.addItem("All Animations", QChart.AllAnimations)
        self.animations_cb.currentIndexChanged.connect(self.changeAnimations)

        self.legend_cb = QComboBox()
        self.legend_cb.addItem("No Legend")
        self.legend_cb.addItem("Align Left", Qt.AlignLeft)
        self.legend_cb.addItem("Align Top", Qt.AlignTop)
        self.legend_cb.addItem("Align Right", Qt.AlignRight)
        self.legend_cb.addItem("Align Bottom", Qt.AlignBottom)
        self.legend_cb.currentTextChanged.connect(self.changeLegend)

        self.antialiasing_check_box = QCheckBox()
        self.antialiasing_check_box.toggled.connect(self.toggleAntialiasing)

        reset_button = QPushButton("Reset Chart Axes")
        reset_button.clicked.connect(self.resetChartZoom)

        # Create table view and set its model
        data_table_view = QTableView()
        data_table_view.setModel(self.model)
        data_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        data_table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)   

        dock_form = QFormLayout()
        dock_form.setAlignment(Qt.AlignTop)
        dock_form.addRow("Themes:", themes_cb)
        dock_form.addRow("Animations:", self.animations_cb)
        dock_form.addRow("Legend:", self.legend_cb)
        dock_form.addRow("Anti-Aliasing", self.antialiasing_check_box)
        dock_form.addRow(reset_button)
        dock_form.addRow(data_table_view)

        # Create QWidget object to act as a container for dock widgets
        tools_container = QWidget()
        tools_container.setLayout(dock_form)
        tools_dock.setWidget(tools_container)

        self.addDockWidget(Qt.LeftDockWidgetArea, tools_dock)
        # Handles the visibility of the dock widget
        self.toggle_dock_tools_act = tools_dock.toggleViewAction()

    def setupWindow(self):
        """The window is comprised of two main parts: A Q3DBars graph on the left, and QToolBox
        on the right containing different widgets for tweaking different settings in the Q3DBars graph."""
        header_label = QLabel("Comparison of Average Monthly Temperatures of Select U.S. Cities 1990-2000 (˚C)")
        header_label.setAlignment(Qt.AlignCenter)

        # Load and prepare the data for the three datasets
        data_files = ["LasVegas_temp.csv", "Spokane_temp.csv", "Richmond_temp.csv"]
        temperature_data = {}
        # Create a dictionary with key, value pairs pertaining to each city and dataset
        for f in data_files:
            data_name = f.split("_")[0] + "_data" # Create a dictionary key for each city
            data = self.loadCSVFile("files/" + f)
    
            # Select 11 years: 1990-2000; the first column in each file is the years
            rows, columns = data.shape
            self.years = data[:, 0]
            monthly_temps = data[:, 1:columns].astype(float)
            temperature_data[data_name] = monthly_temps

        bar_graph = Q3DBars() # Create instance for bar graph
        bar_graph.setMultiSeriesUniform(True) # Bars are scaled proportionately
        bar_graph.scene().activeCamera().setCameraPreset(Q3DCamera.CameraPresetFront)

        # Create lists of QBarDataItem objects for each city 
        vegas_data_items = []
        for row in temperature_data["LasVegas_data"]:
            vegas_data_items.append([QBarDataItem(value) for value in row])

        spokane_data_items = []
        for row in temperature_data["Spokane_data"]:
            spokane_data_items.append([QBarDataItem(value) for value in row])
    
        richmond_data_items = []
        for row in temperature_data["Richmond_data"]:
            richmond_data_items.append([QBarDataItem(value) for value in row])

        self.months = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"]

        # Create instances of QBar3DSeries for each set of data; dataProxy() handles 
        # modifying data in the series
        vegas_series = QBar3DSeries()
        vegas_series.dataProxy().addRows(vegas_data_items)
        vegas_series.dataProxy().setRowLabels(self.years) # rowLabel
        vegas_series.dataProxy().setColumnLabels(self.months) # colLabel

        spokane_series = QBar3DSeries()
        spokane_series.dataProxy().addRows(spokane_data_items)

        richmond_series = QBar3DSeries()
        richmond_series.dataProxy().addRows(richmond_data_items)

        # Create the valueLabel
        temperature_axis = QValue3DAxis()
        temperature_axis.setRange(-10, 40)
        temperature_axis.setLabelFormat(u"%.1f \N{degree sign}C")
        bar_graph.setValueAxis(temperature_axis)

        # Set the format for the labels that appear when items are clicked on
        vegas_series.setItemLabelFormat("LasVegas - @colLabel @rowLabel: @valueLabel")
        spokane_series.setItemLabelFormat("Spokane - @colLabel @rowLabel: @valueLabel")
        richmond_series.setItemLabelFormat("Richmond - @colLabel @rowLabel: @valueLabel")

        # Add the three series to the bar graph
        bar_graph.setPrimarySeries(vegas_series)
        bar_graph.addSeries(spokane_series)
        bar_graph.addSeries(richmond_series)

        # Create a QWidget to hold only the graph
        graph_container = QWidget.createWindowContainer(bar_graph)
        main_h_box = QHBoxLayout() # Main layout for the entire window
        graph_v_box = QVBoxLayout() # Layout that holds the graph
        graph_v_box.addWidget(header_label)
        graph_v_box.addWidget(graph_container, 1)

        ##############################################################################
        # The following section creates the QToolBox that appears on the
        # right of the window and contains widgets for interacting with the graph
        self.modifier = GraphModifier(self, bar_graph) # Create modifier instance

        settings_toolbox = QToolBox()
        settings_toolbox.setFixedWidth(300)
        settings_toolbox.setCurrentIndex(0) # Show the first tab

        # The first tab - Widgets for rotating the bar graph and changing the camera
        horizontal_rotation_slider = QSlider(Qt.Horizontal)
        horizontal_rotation_slider.setTickInterval(20)
        horizontal_rotation_slider.setRange(-180, 180)
        horizontal_rotation_slider.setValue(0)
        horizontal_rotation_slider.setTickPosition(QSlider.TicksBelow)
        horizontal_rotation_slider.valueChanged.connect(self.modifier.rotateHorizontal)
        
        vertical_rotation_slider = QSlider(Qt.Horizontal)
        vertical_rotation_slider.setTickInterval(20)
        vertical_rotation_slider.setRange(-180, 180)
        vertical_rotation_slider.setValue(0)
        vertical_rotation_slider.setTickPosition(QSlider.TicksBelow)
        vertical_rotation_slider.valueChanged.connect(self.modifier.rotateVertical)

        # QPushButton for changing the camera's view point
        camera_view_button = QPushButton("Change Camera View")
        camera_view_button.clicked.connect(self.modifier.changeCameraView)

        # Layout for the View tab (first tab)
        view_tab_container = QWidget()
        view_tab_v_box = QVBoxLayout()
        view_tab_v_box.setAlignment(Qt.AlignTop)
        view_tab_v_box.addWidget(QLabel("Rotate Horizontally"))
        view_tab_v_box.addWidget(horizontal_rotation_slider)
        view_tab_v_box.addWidget(QLabel("Rotate Vertically"))
        view_tab_v_box.addWidget(vertical_rotation_slider)
        view_tab_v_box.addWidget(camera_view_button)
        view_tab_container.setLayout(view_tab_v_box)

        settings_toolbox.addItem(view_tab_container, "View")

        # The second tab - Widgets for changing the appearance of the graph. Recheck the  
        # background and grid checkboxes if the theme has changed
        show_background_cb = QCheckBox("Show Background")
        show_background_cb.setChecked(True)
        show_background_cb.stateChanged.connect(self.modifier.showOrHideBackground)
        self.modifier.background_selected.connect(show_background_cb.setChecked)

        show_grid_cb = QCheckBox("Show Grid")
        show_grid_cb.setChecked(True)
        show_grid_cb.stateChanged.connect(self.modifier.showOrHideGrid)
        self.modifier.grid_selected.connect(show_grid_cb.setChecked)

        smooth_bars_cb = QCheckBox("Smoothen Bars")
        smooth_bars_cb.stateChanged.connect(self.modifier.smoothenBars)

        # QComboBox for selecting the Qt theme
        themes = ["Qt", "Primary Colors", "Digia", "Stone Moss", "Army Blue",
            "Retro", "Ebony", "Isabelle"]
        select_theme_combo = QComboBox()
        select_theme_combo.addItems(themes)
        select_theme_combo.setCurrentIndex(0)
        select_theme_combo.currentIndexChanged.connect(self.modifier.changeTheme)

        # QComboBox for selecting the visual style of the bars
        bar_style_combo = QComboBox()
        bar_style_combo.addItem("Bar", QAbstract3DSeries.MeshBar)
        bar_style_combo.addItem("Pyramid", QAbstract3DSeries.MeshPyramid)
        bar_style_combo.addItem("Cylinder", QAbstract3DSeries.MeshCylinder)        
        bar_style_combo.addItem("Sphere", QAbstract3DSeries.MeshSphere)
        bar_style_combo.setCurrentIndex(0)
        bar_style_combo.currentIndexChanged.connect(self.modifier.changeBarStyle)

        # Layout for the Style tab (second tab)
        style_tab_container = QWidget()
        style_tab_v_box = QVBoxLayout()
        style_tab_v_box.setAlignment(Qt.AlignTop)
        style_tab_v_box.addWidget(show_background_cb)
        style_tab_v_box.addWidget(show_grid_cb)
        style_tab_v_box.addWidget(smooth_bars_cb)
        style_tab_v_box.addWidget(QLabel("Select Qt Theme"))
        style_tab_v_box.addWidget(select_theme_combo)
        style_tab_v_box.addWidget(QLabel("Select Bar Style"))
        style_tab_v_box.addWidget(bar_style_combo)
        style_tab_container.setLayout(style_tab_v_box)

        settings_toolbox.addItem(style_tab_container, "Style")

        # The third tab - Widgets for hiding/showing different series and changing how 
        # items are viewed and selected
        second_series_cb = QCheckBox("Show Second Series")
        second_series_cb.setChecked(True)
        second_series_cb.stateChanged.connect(self.modifier.showOrHideSeries)

        third_series_cb = QCheckBox("Show Third Series")
        third_series_cb.setChecked(True)
        third_series_cb.stateChanged.connect(self.modifier.showOrHideSeries)

        # QComboBox for changing how items in the bar graph are selected
        selection_mode_combo = QComboBox()
        selection_mode_combo.addItem("None", QAbstract3DGraph.SelectionNone)
        selection_mode_combo.addItem("Bar", QAbstract3DGraph.SelectionItem)
        selection_mode_combo.addItem("Row", QAbstract3DGraph.SelectionRow)
        selection_mode_combo.addItem("Column", QAbstract3DGraph.SelectionColumn)
        selection_mode_combo.addItem("Item, Row, Column", QAbstract3DGraph.SelectionItemRowAndColumn)
        selection_mode_combo.setCurrentIndex(1)
        selection_mode_combo.currentIndexChanged.connect(self.modifier.changeSelectionStyle)

        # QComboBox for selecting which years to view
        select_year_combo = QComboBox()
        select_year_combo.addItems(self.years)
        select_year_combo.addItem("All Years")
        select_year_combo.setCurrentIndex(len(self.years))
        select_year_combo.currentIndexChanged.connect(self.modifier.selectYears)

        # QComboBox for selecting which months to view
        select_month_combo = QComboBox()
        select_month_combo.addItems(self.months)
        select_month_combo.addItem("All Months")
        select_month_combo.setCurrentIndex(len(self.months))
        select_month_combo.currentIndexChanged.connect(self.modifier.selectMonths)    

        # Layout for the Selection tab (third tab)
        selection_tab_container = QWidget()
        selection_tab_v_box = QVBoxLayout()
        selection_tab_v_box.addWidget(second_series_cb)
        selection_tab_v_box.addWidget(third_series_cb)
        selection_tab_v_box.addWidget(QLabel("Choose Selection Mode"))
        selection_tab_v_box.addWidget(selection_mode_combo)
        selection_tab_v_box.addWidget(QLabel("Select Year"))
        selection_tab_v_box.addWidget(select_year_combo)
        selection_tab_v_box.addWidget(QLabel("Select Month"))
        selection_tab_v_box.addWidget(select_month_combo)
        selection_tab_container.setLayout(selection_tab_v_box)

        settings_toolbox.addItem(selection_tab_container, "Selection") 

        # Set up the layout for the settings toolbox
        settings_v_box = QVBoxLayout()
        settings_v_box.addWidget(settings_toolbox, 0, Qt.AlignTop)

        main_h_box.addLayout(graph_v_box)
        main_h_box.addLayout(settings_v_box)

        main_widget = QWidget()
        main_widget.setLayout(main_h_box)
        self.setCentralWidget(main_widget)

    def loadCSVFile(self, file_name):
        """Load CSV files. Return data as numpy arrays."""
        with open(file_name, "r") as csv_f:
            reader = csv.reader(csv_f)
            header_labels = next(reader)
            data = np.array(list(reader))
        return data

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = SimpleBarGraph()
    sys.exit(app.exec_())