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
        self.MUT = motor
        self.load_motor = motor
        self.transducer = transducer
        self.view = view

    def open_connection(self) -> None:
        try:
            self.server.open()
        except Exception as e:
            print(f"Failed to open connection: {e}")
            self.view.open_connection_window(self, self.server.com_port)

    def get_current_COM(self) -> None:
        ports = self.server.list_ports()
        if ports.type is None:
            raise Exception("No COM ports found.")
        else:
            return ports

    def command_MUT_rpm(self) -> None:
        self.MUT.set_rpm(self.view.get_rpm())

    def read_MUT_speed(self, event=None) -> None:
        task = self.view.get_plot_type()
        self.view.clear_entry()
        self.model.add_task(task)
        self.update_task_list()

    def run(self) -> None:
        self.view.init_ui(self)
        self.view.mainloop()
        self.view.show()
