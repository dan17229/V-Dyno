import pyqtgraph.examples
pyqtgraph.examples.run()

# # Example sourced from Rob Kent (@jazzycamel) and modified for PyQtGraph purposes
# # https://gist.github.com/jazzycamel/8abd37bf2d60cce6e01d
# # SPDX-License-Identifier: MIT
# from itertools import count, islice
# import sys

# from PyQt6.QtCore import *
# from PyQt6.QtWidgets import *


# class Threaded(QObject):
#     result=pyqtSignal(int)

#     def __init__(self, parent=None, **kwargs):
#         # intentionally not setting the parent
#         super().__init__(parent=None, **kwargs)

#     @pyqtSlot()
#     def start(self):
#         print("Thread started")

#     @pyqtSlot(int)
#     def calculatePrime(self, n):
#         primes=(n for n in count(2) if all(n % d for d in range(2, n)))
#         # sends the result across threads
#         self.result.emit(list(islice(primes, 0, n))[-1])

# class Window(QWidget):
#     requestPrime=pyqtSignal(int)

#     def __init__(self, parent=None, **kwargs):
#         super().__init__(parent, **kwargs)

#         self._thread = QThread()
#         # important to *not* set a parent, or .moveToThread will silently fail
#         self._threaded = Threaded()
#         self._threaded.result.connect(self.displayPrime)
#         self.requestPrime.connect(self._threaded.calculatePrime)
#         self._thread.started.connect(self._threaded.start)
#         self._threaded.moveToThread(self._thread)

#         qApp = QApplication.instance()
#         if qApp is not None:
#             qApp.aboutToQuit.connect(self._thread.quit)
#         self._thread.start()

#         layout = QVBoxLayout(self)
#         self._iterationLineEdit = QLineEdit(
#             self,
#             placeholderText="Iteration (n)"
#         )
#         layout.addWidget(self._iterationLineEdit)
#         self._requestButton = QPushButton(
#             "Calculate Prime",
#             self,
#             clicked=self.primeRequested
#         )
#         layout.addWidget(self._requestButton)
#         self._busy = QProgressBar(self)
#         layout.addWidget(self._busy)
#         self._resultLabel=QLabel("Result:", self)
#         layout.addWidget(self._resultLabel)

#     @pyqtSlot()
#     def primeRequested(self):
#         try:
#             n = int(self._iterationLineEdit.text())
#         except ValueError:
#             # ignore input that can't be cast to int
#             return
#         self.requestPrime.emit(n)
#         self._busy.setRange(0, 0)
#         self._iterationLineEdit.setEnabled(False)
#         self._requestButton.setEnabled(False)

#     @pyqtSlot(int)
#     def displayPrime(self, prime):
#         self._resultLabel.setText(f"Result: {prime}")
#         self._busy.setRange(0, 100)
#         self._iterationLineEdit.setEnabled(True)
#         self._requestButton.setEnabled(True)

# if __name__=="__main__":
#     a = QApplication(sys.argv)
#     g = Window()
#     g.show()
#     sys.exit(a.exec())