import serial
import can
import cantools
import serial.tools.list_ports


def list_ports() -> list:
    ports = serial.tools.list_ports.comports()
    port_list = []
    for port in ports:
        port_list.append(port.device)
    return port_list


class CANHandler:
    def __init__(self) -> None:
        self.com_port = None
        self.can_bus = None
        self.tester = None
        self.detect_port()
        self.database = self.get_dbc()
        self.open(self.database, self.com_port)

    def detect_port(self) -> None:
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "USB-SERIAL CH340" in port.description:
                self.com_port = port.device
                break
        else:
            raise Exception("USB-SERIAL CH340 not found")

    def get_dbc(self) -> None:
        self.database = cantools.db.load_file("CAN/VESC.dbc")

    def open(self) -> None:
        _can_bus = can.interface.Bus(
            interface="seeedstudio",
            channel=self.com_port,
            baudrate=2000000,
            bitrate=500000,
        )
        self.tester = cantools.tester.Tester("VESC1", self.database, _can_bus)
        self.tester.start()

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

    def send(self, message: object) -> None:
        self.tester.send(message)

    def flush_input(self) -> None:
        self.tester.flush_input()

    def expect(self, message: object, timeout: float) -> object|None:
        message = self.tester.expect(message, None, timeout, discard_other_messages=True)
        return message

    def close(self) -> None:
        self.can_bus.shutdown()

if __name__ == "__main__":
    try:
        connection_handler = CANHandler()
    except Exception as e:
        print(f"Error: {e}")
        print(list_ports())