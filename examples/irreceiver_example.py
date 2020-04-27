#!/usr/bin/env python3
"""
This is a simple example where pigpio on a Raspberry Pi is used to monitor the IR signal.
The pigpio program detects the events, PiPulseCollector collects them and the NecDecoder decodes them.
Please see the pigpio for information on how to set it up.
Other code would be placed in the try block which keeps this from exiting on the Pi.
"""

import time
from typing import Callable

import pigpio

import irreceiver


class PiPulseCollector:
    """
    This class collects the timing between IR pulses
    """
    def __init__(self, pi: pigpio.pi, receive_pin: int,
                 done_callback: Callable, max_time: int,
                 decoder: irreceiver.NecDecoder):
        self.pi = pi
        self.receive_pin = receive_pin
        self.done_callback = done_callback
        self.max_time = max_time
        self.decoder = decoder

        self.t1 = None
        self.t2 = None
        self.pulse_times = []
        self.collecting = False

    def collect_pulses(self, _, level: int, tick: int):
        """
        This function adds a pulse to self.pulse_times
        Once the allowed time has elapsed the decode callback is called and then (if valid) the done_callback

        Args:
            _: (unused) The pin number is automatically passed by the pigpio callback
            level: pigpo denotes a falling edge with 0, a rising edge with 1 and a timeout by pigpo.TIMEOUT
            tick: The number of microseconds between boot and this event
        """

        if level != pigpio.TIMEOUT:
            if not self.collecting:
                self.pulse_times = []
                self.collecting = True
                self.pi.set_watchdog(self.receive_pin, self.max_time)
                self.t1 = None
                self.t2 = tick

            else:
                self.t1 = self.t2
                self.t2 = tick

                if self.t1 is not None:
                    pulse_time = pigpio.tickDiff(self.t1, self.t2)
                    self.pulse_times.append(pulse_time)

        # Receive time is done
        else:
            if self.collecting:
                self.collecting = False
                self.pi.set_watchdog(self.receive_pin, 0)
                self.done_callback(self.decoder.decode(self.pulse_times))


def ir_callback(code: int):
    """
    Simple demonstration callback function
    In this example it is called by the PulseCollector when the signal has been successfully decoded

    Args:
        code: The decoded signal
    """

    print('Invalid code') if code == irreceiver.INVALID_FRAME else print(
        hex(code))


def main():
    """Run a simple example that prints IR codes received on a Raspberry PI"""

    # Set up GPIO on raspberry pi
    ir_pin = 14
    pi = pigpio.pi()
    pi.set_mode(ir_pin, pigpio.INPUT)

    decoder = irreceiver.NecDecoder()
    collector = PiPulseCollector(
        pi, ir_pin, ir_callback,
        irreceiver.FRAME_TIME_MS + irreceiver.TIMING_TOLERANCE, decoder)
    _ = pi.callback(ir_pin, pigpio.EITHER_EDGE, collector.collect_pulses)

    print('Press Ctrl-c to exit')

    try:
        # Do something here

        while True:
            time.sleep(300)

    except KeyboardInterrupt:
        print('Stopping')
        pi.stop()


if __name__ == "__main__":
    main()
