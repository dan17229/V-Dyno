from typing import Protocol


class can_server_handler(Protocol):
    def send(self, message: object) -> None:
        """Send a message to the CAN server."""


class Motor:
    def __init__(self, can_sever: can_server_handler, vesc_number: int) -> None:
        self.model = can_sever
        self.vesc_number = vesc_number

    def set_rpm(self, rpm_value: int) -> None:
        message = (
            f"VESC_Command_RelCurrent_V{self.vesc_number}",
            {f"Command_RelativeCurrent_V{self.vesc_number}": rpm_value},
        )
        self.model.send(message)

    def set_brake_current(self, brake_current: float) -> None:
        message = (
            f"VESC_Command_AbsBrakeCurrent_V{self.vesc_number}",
            {f"Command_BrakeCurrent_V{self.vesc_number}": brake_current},
        )
        self.model.send(message)
    
    @property
    def status(self) -> dict|None:
        self.model.flush_input()
        return self.model.expect(f'VESC_Status1_V{self.vesc_number}', timeout=.01)

class TorqueTransducer:
    def __init__(self, can_server: can_server_handler) -> None:
        self.model = can_server

    @property
    def status(self) -> dict|None:
        self.model.flush_input()
        return self.model.expect('TEENSY_Status', timeout=.01)
    
class Dyno:
    def __init__(self) -> None:
        can_server = CANHandler()
        self.MUT = Motor(can_server, 1)
        self.load_motor = Motor(can_server, 2)
        self.torque_transducer = TorqueTransducer(can_server)
        
if __name__ == "__main__":
    from can_handler import CANHandler
    dyno = Dyno(CANHandler())
