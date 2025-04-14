from typing import Protocol

if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from VDyno.model.dummy_can_handler import CANHandler

class can_server_handler(Protocol):
    def send(self, message: object) -> None: ...


class Motor:
    def __init__(self, can_server: can_server_handler, vesc_number: int) -> None:
        self.model = can_server
        self.vesc_number = vesc_number
        self.status = None

    def set_rpm(self, rpm_value: int) -> None:
        message_name = f"VESC_Command_RPM_V{self.vesc_number}"
        signals = {f"Command_RPM_V{self.vesc_number}": rpm_value}
        self.model.send(message_name, signals)

    def set_current(self, current_value: int) -> None:
        message_name = f"VESC_Command_AbsCurrent_V{self.vesc_number}"
        signals = {f"Command_Current_V{self.vesc_number}": current_value}
        self.model.send(message_name, signals)

    def set_brake_current(self, brake_current: float) -> None:
        message_name = f"VESC_Command_AbsBrakeCurrent_V{self.vesc_number}"
        signals = {f"Command_BrakeCurrent_V{self.vesc_number}": brake_current}
        self.model.send(message_name, signals)

    def update_status(self) -> None:
        self.model.flush_input()
        status = self.model.expect(f"VESC_Status1_V{self.vesc_number}", timeout=0.021)
        if status is not None:
            self.status = status


class TorqueTransducer:
    def __init__(self, can_server: can_server_handler) -> None:
        self.model = can_server
        self.status = None

    def update_status(self) -> None:
        self.model.flush_input()
        status = self.model.expect("TEENSY_Status", timeout=0.02)
        if status is not None:
            self.status = status

class Dyno:
    def __init__(self) -> None:
        can_server = CANHandler()
        self.MUT = Motor(can_server, 1)
        self.load_motor = Motor(can_server, 2)
        self.torque_transducer = TorqueTransducer(can_server)


if __name__ == "__main__":
    dyno = Dyno()
