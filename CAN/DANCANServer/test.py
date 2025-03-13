#!/usr/bin/env python3
#
# Script testing the motor.
#

import os
import can
import matplotlib.pyplot as plt
import serial.tools.list_ports
import cantools
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
ports = list(serial.tools.list_ports.comports())
for port in ports:
    if 'USB-SERIAL CH340' in port.description:
        com_port = port.device
        break
else:
    raise Exception("USB-SERIAL CH340 not found")

print(f"Found USB-SERIAL CH340 on {com_port}")

can_bus = can.interface.Bus(interface='seeedstudio',
                            channel=com_port,
                            baudrate=2000000,
                            bitrate=500000)

database = cantools.db.load_file("VESC.dbc")
tester = cantools.tester.Tester('VESC1',
                                database,
                                can_bus)
tester.start()

while True:
    tester.send('VESC_Command_RPM_V1', {'Command_RPM_V1': 1000})
    time.sleep(.5)
    status = tester.expect('VESC_Status1_V1', None, timeout=.1, discard_other_messages=True)
    if status is not None:
        status['Status_TotalCurrent_V1'] /= 10
        print('VESC1: {Status_RPM_V1} rpm, {Status_TotalCurrent_V1}A'.format(**status))


