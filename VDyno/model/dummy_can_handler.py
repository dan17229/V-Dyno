from serial.tools import list_ports
import cantools
from random import randint

def list_COM_ports() -> list:
    ports = list_ports.comports()
    port_list = []
    for port in ports:
        port_list.append(port.device)
    return port_list


class CANHandler:
    def __init__(self) -> None:
        self.detect_port()
        self.database = self.get_dbc()
        self.open()
        self.MUT_speed = 0
        self.MUT_brake_current = 0
        self.load_speed = 0
        self.load_brake_current = 0
        self.transducer_torque = 0

    def detect_port(self) -> None:
        print("Detecting COM port...")

    def get_dbc(self) -> None:
        self.database = cantools.db.load_file("VDyno/model/CAN/VESC.dbc")

    def open(self) -> None:
        print("Opening CAN bus...")

    def send(self, message_name:str, signals:dict) -> None:
        print(f"Sending message: {message_name}, signals: {signals}")

    def flush_input(self) -> None:
        ...#print("Flushing input...")

    def expect(self, message_name: object, timeout: float) -> object|None:
        if message_name == "VESC_Status1_V1":
            self.MUT_speed =  self.MUT_speed + randint(-100, 100)
            self.MUT_brake_current = self.MUT_brake_current + randint(-1, 1)
            message = {"Status_RPM_V1": self.MUT_speed, "Status_TotalCurrent_V1": self.MUT_brake_current}
        elif message_name == "VESC_Status1_V2":
            self.load_speed =  self.MUT_speed + randint(-100, 100)
            self.load_brake_current = self.MUT_brake_current + randint(-1, 1)
            message = {"Status_RPM_V2": self.MUT_speed, "Status_TotalCurrent_V2": self.MUT_brake_current}
        elif message_name == "TEENSY_Status":
            self.transducer_torque =  self.transducer_torque + randint(-100, 100)
            message = {"TorqueValue": self.transducer_torque}

        return message

    def close(self) -> None:
        print("Closing CAN bus...")

if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    try:
        connection_handler = CANHandler()
    except Exception as e:
        print(f"Error: {e}")
        print(list_COM_ports())