#!/usr/bin/env python

"""
This example shows how sending a single message works.
"""

import can


def send_one():
    """Sends a single message."""

    # this uses the default configuration (for example from the config file)
    # see https://python-can.readthedocs.io/en/stable/configuration.html
    with can.Bus(interface='InnoMaker', channel='0', bitrate=250000) as bus:

        msg = can.Message(
            arbitration_id=1, data=[0, 25, 0, 1, 3, 1, 4, 1], is_extended_id=True
        )

        try:
            bus.send(msg)
            print(f"Message sent on {bus.channel_info}")
        except can.CanError:
            print("Message NOT sent")


if __name__ == "__main__":
    send_one()