"""
This module contains the CANCapture class which is used to capture CAN messages from the CAN bus.
author Daniel Muir <danielmuir167@gmail.com>
"""

from PyQt6 import QObject, pyqtSignal, pyqtSlot, QtCore

class CANCapture(QObject):
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
            status_V1 = tester.expect('VESC_Status1_V1', None, timeout=.01, discard_other_messages=True)
            status_V2 = tester.expect('VESC_Status1_V1', None, timeout=.01, discard_other_messages=True)
            status_TT = tester.expect('TEENSY_Status', None, timeout=.01, discard_other_messages=True)
            if status_V1 is not None:
                self.V1_status.emit(status_V1)
            if status_V2 is not None:
                self.V2_status.emit(status_V2)
            if status_TT is not None:
                self.TT_status.emit(status_TT)
            QtCore.QThread.msleep(10)  # sleep for a short duration to prevent high CPU usage