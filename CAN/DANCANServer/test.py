#!/usr/bin/env python3
#
# Script testing the motor.
#

import os
import can
import matplotlib.pyplot as plt
import cantools
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

can_bus = can.interface.Bus(interface='seeedstudio',
                            channel='COM9',
                            baudrate=2000000,
                            bitrate=500000)

database = cantools.db.load_file("VESC.dbc")
tester = cantools.tester.Tester('VESC1',
                                database,
                                can_bus)
tester.start()

while True:
    tester.send('VESC_Command_RPM_V1', {'Command_RPM_V1': 1500})
    status = tester.expect('VESC_Status1_V1', None, timeout=.2, discard_other_messages=True)
    print('Motor speed is {Status_RPM_V1} rpm and load is {Status_TotalCurrent_V1}%.'.format(**status))

