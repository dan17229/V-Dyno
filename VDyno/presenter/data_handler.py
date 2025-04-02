from __future__ import annotations

from typing import Protocol

from VDyno.model.model import Motor, TorqueTransducer
from VDyno.model.can_handler import CANHandler


class View(Protocol):
    def init_ui(self, presenter: Presenter) -> None: ...

    def change_plot_type(self) -> str: ...

    @property
    def selected_task(self) -> str: ...

    def mainloop(self) -> None: ...


class Presenter:
    def __init__(
        self, server: CANHandler, motor: Motor, transducer: TorqueTransducer, view: View
    ) -> None:
        self.server = server
        self.MUT = Motor
        self.load_motor = Motor
        self.transducer = TorqueTransducer
        self.view = view

    def handle_add_task(self, event=None) -> None:
        task = self.view.get_entry_text()
        self.view.clear_entry()
        self.model.add_task(task)
        self.update_task_list()


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
