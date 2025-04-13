from __future__ import annotations
from typing import Protocol
# from PyQt6.QtCore import pyqtSignal, QThread, pyqtSlot

if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from VDyno.model.dyno import Dyno

class View(Protocol):
    def init_ui(self, presenter: Presenter) -> None: ...


class Presenter:
    def __init__(self, dyno: Dyno, view: View) -> None:
        self.dyno = dyno
        self.view = view
        self.MUT_key = "rpm"
        self.load_motor_key = "brake_current"
        self.transducer_key = "torque"

    def command_MUT_rpm(self) -> None:
        self.dyno.MUT.set_rpm(self.view.get_rpm())

    def command_load_brake_current(self) -> None:
        self.dyno.load_motor.set_brake_current(self.view.get_brake_current())

    def update_MUT_plot(self) -> None:
        status = self.dyno.MUT.status
        value = status[self.MUT_key]
        self.view.update_MUT_plot(value)

    def update_load_motor_plot(self) -> None:
        status = self.dyno.load_motor.status
        value = status[self.load_motor_key]
        self.view.update_load_motor_plot(value)

    def update_transducer_plot(self) -> None:
        status = self.dyno.torque_transducer.status
        value = status[self.transducer_key]
        self.view.update_transducer_plot(value)

    def run(self) -> None:
        self.view.init_ui(self)
        self.update_status()