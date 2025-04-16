import csv
from typing import Protocol

if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from VDyno.model.can_handler import CANHandler


class can_server_handler(Protocol):
    def send(self, message: object) -> None: ...
    def flush_input(self) -> None: ...
    def expect(self, message: str, timeout: float) -> dict: ...


def load_calibration(file_path: str) -> dict:
    calibration_data = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row['name']
            factor = float(row['factor'])
            offset = float(row['offset'])
            calibration_data[key] = {'factor': factor, 'offset': offset}
    return calibration_data


class Motor:
    def __init__(self, can_server: can_server_handler, vesc_number: int, calibration_file: str) -> None:
        self.model = can_server
        self.vesc_number = vesc_number
        self.status = {f"Status_RPM_V{vesc_number}": 0, f"Status_TotalCurrent_V{vesc_number}": 0, f"Status_DutyCycle_V{vesc_number}": 0}
        self.calibration = load_calibration(calibration_file)

    def set_rpm(self, rpm_value: int) -> None:
        # Apply inverse scaling and offset if calibration exists
        key = f"Status_RPM_V{self.vesc_number}"
        if key in self.calibration:
            factor = self.calibration[key]['factor']
            offset = self.calibration[key]['offset']
            rpm_value = int((rpm_value - offset) / factor)

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
            scaled_status = {}
            for key, value in status.items():
                if key in self.calibration:
                    factor = self.calibration[key]['factor']
                    offset = self.calibration[key]['offset']
                    scaled_status[key] = value * factor + offset
                else:
                    scaled_status[key] = value
            self.status = scaled_status


class TorqueTransducer:
    def __init__(self, can_server: can_server_handler, calibration_file: str) -> None:
        self.model = can_server
        self.status = {"TorqueValue": 0}
        self.calibration = load_calibration(calibration_file)

    def update_status(self) -> None:
        self.model.flush_input()
        status = self.model.expect("TEENSY_Status", timeout=0.02)
        if status is not None:
            scaled_status = {}
            for key, value in status.items():
                if key in self.calibration:
                    factor = self.calibration[key]['factor']
                    offset = self.calibration[key]['offset']
                    scaled_status[key] = value * factor + offset
                else:
                    scaled_status[key] = value
            self.status = scaled_status


class Dyno:
    def __init__(self) -> None:
        can_server = CANHandler()
        calibration_file = "VDyno/model/value_calibration.csv"
        self.MUT = Motor(can_server, 1, calibration_file)
        self.load_motor = Motor(can_server, 2, calibration_file)
        self.torque_transducer = TorqueTransducer(can_server, calibration_file)


if __name__ == "__main__":
    dyno = Dyno()
