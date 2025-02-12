from test_thresholds import *
from __main__ import *  # to use the single_send and receive functions in main 

def tc_1():
    ct = receive(0x300, 'ct_signal')  # this is where the issue occurs. receive expects the bus instance
    message = can.Message(arbitration_id=0x303, data=1)
    if (ct > ct_min) and (ct < ct_max):
        verbose_log.write("PASS")
    else:
        verbose_log.write("FAIL")