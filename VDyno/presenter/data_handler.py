from __future__ import annotations
from typing import Protocol
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtWidgets import QApplication
from time import sleep

if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from VDyno.model.dyno import Dyno

class View(Protocol):
    def init_ui(self, presenter: Presenter) -> None: ...

class ThreadedDataFetcher(QObject):
    MUT_status_signal = pyqtSignal(dict)
    load_motor_status_signal = pyqtSignal(dict)
    torque_transducer_status_signal = pyqtSignal(dict)

    def __init__(self, dyno: Dyno) -> None:
        super().__init__()
        self.dyno = dyno
        self.running = True

    @pyqtSlot()
    def start(self):
        print("Thread started") 
        while self.running:
            for status, signal in [
            (self.dyno.MUT.status, self.MUT_status_signal),
            (self.dyno.load_motor.status, self.load_motor_status_signal),
            (self.dyno.torque_transducer.status, self.torque_transducer_status_signal),
            ]:
                if status is not None:
                    signal.emit(status)
            sleep(.02)

class Presenter:
    def __init__(self, dyno: Dyno, view: View) -> None:
        self.dyno = dyno
        self.view = view
        self.motor_keys = ["rpm", "brake_current"]
        self.transducer_keys = ["torque"]
        self.MUT_key = 0
        self.load_motor_key = 1
        self.transducer_key = 0

    def command_MUT_rpm(self) -> None:
        self.dyno.MUT.set_rpm(self.view.get_rpm())

    def command_load_brake_current(self) -> None:
        self.dyno.load_motor.set_brake_current(self.view.get_brake_current())

    def update_MUT_plot(self) -> None:
        status = self.dyno.MUT.status
        value = status[self.motor_keys[self.MUT_key]]
        self.view.update_MUT_plot(value)

    def update_load_motor_plot(self) -> None:
        status = self.dyno.load_motor.status
        value = status[self.motor_keys[self.load_motor_key]]
        self.view.update_load_motor_plot(value)

    def update_transducer_plot(self) -> None:
        status = self.dyno.torque_transducer.status
        value = status[self.transducer_keys[self.transducer_key]]
        self.view.update_transducer_plot(value)

    def plot_MUT_changed(self, key:int) -> None:
        self.MUT_key = key
    
    def plot_load_changed(self, key:int) -> None:
        self.load_motor_key = key

    def plot_TT_changed(self, key:int) -> None:
        self.transducer_key = key
    
    def setup_thread(self):
        self._thread = QThread()
        self._threaded = ThreadedDataFetcher(self.dyno)
        self._threaded.MUT_status_signal.connect(self.update_MUT_plot)
        self._threaded.load_motor_status_signal.connect(self.update_load_motor_plot)
        self._threaded.torque_transducer_status_signal.connect(self.update_transducer_plot)
        self._thread.started.connect(self._threaded.start)
        self._threaded.moveToThread(self._thread)
        # Stop the thread once the app is closed
        QApplication.instance().aboutToQuit.connect(self._thread.quit)
        print("Thread setup complete")
        self._thread.start()

    def run(self) -> None:
        print("Starting Thread")
        self.setup_thread()
        print("Running the presenter")
        self.view.init_UI(self)
