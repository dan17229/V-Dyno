import os

# Change the working directory to the directory of the script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import can
import cantools
import test_cases.test_cases
import time

# sending a single CAN message
def single_send(message):
    try:
        bus.send(message)
    except can.CanError:
        print("Message NOT sent")


# receive a message and decode payload
def receive(message, signal):
    _counter = 0
    try:
        while True:
            msg = bus.recv(1)
            try:
                if msg.arbitration_id == message.arbitration_id:
                    message_data = db.decode_message(msg.arbitration_id, msg.data)
                    signal_data = message_data.get(signal)
                    return signal_data
            except AttributeError:
                _counter += 1
                if _counter == 5:
                    print("CAN Bus InActive")
                    break
    finally:
        if _counter == 5:
            # reports false if message fails to be received
            return False

def main():
    for name, tests in test_cases.test_cases.__dict__.items():
        if name.startswith("tc") and callable(tests):
            tests()


if __name__ == "__main__":
    bus = can.Bus(interface='seeedstudio',
                            channel='COM9',
                            baudrate=2000000,
                            bitrate=500000)
    db = cantools.db.load_file('VESC.dbc')
    verbose_log = open("verbose_log.txt", "a")
    main()
    bus.shutdown()
    verbose_log.close()