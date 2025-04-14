import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

app = pg.mkQApp()

view = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()
pg.setConfigOptions(antialias=True)  ## this will be expensive for the local plot
view.pg.setConfigOptions(antialias=True)  ## prettier plots at no cost to the main process! 
view.setWindowTitle('pyqtgraph example: RemoteSpeedTest')

app.aboutToQuit.connect(view.close)

label = QtWidgets.QLabel()
rcheck = QtWidgets.QCheckBox('plot remote')
rcheck.setChecked(True)
lcheck = QtWidgets.QCheckBox('plot local')
lplt = pg.PlotWidget()
layout = pg.LayoutWidget()
layout.addWidget(rcheck)
layout.addWidget(lcheck)
layout.addWidget(label)
layout.addWidget(view, row=1, col=0, colspan=3)
layout.addWidget(lplt, row=2, col=0, colspan=3)
layout.resize(800,800)
layout.show()

## Create a PlotItem in the remote process that will be displayed locally
rplt = view.pg.PlotItem()
rplt._setProxyOptions(deferGetattr=True)  ## speeds up access to rplt.plot
view.setCentralItem(rplt)

def update():

    data = np.random.normal(size=(10000,50)).sum(axis=1)
    data += 5 * np.sin(np.linspace(0, 10, data.shape[0]))
    
    if rcheck.isChecked():
        rplt.plot(data, clear=True, _callSync='off')  ## We do not expect a return value.
                                                      ## By turning off callSync, we tell
                                                      ## the proxy that it does not need to 
                                                      ## wait for a reply from the remote
                                                      ## process.
    if lcheck.isChecked():
        lplt.plot(data, clear=True)
        
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)

if __name__ == '__main__':
    pg.exec()
