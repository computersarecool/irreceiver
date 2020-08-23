"""
This is a class to parse the NEC IR remote protocol.

A reference for the protocol can be found at https://www.sbprojects.net/knowledge/ir/nec.php
"""

INVALID_FRAME = -1
REPEAT_MESSAGE = 0
NEW_MESSAGE = 1
FRAME_TIME_MS = 67.5
TIMING_TOLERANCE = .3125


class NecDecoder:
    """
    Decode an NEC protocol message.
    A single integer is returned where the first eight bits are the address and the second eight are the command.
    Most member variables come from the spec except timing_tolerance which was found empirically
    """
    def __init__(self,
                 extended_protocol=False,
                 time_tolerance=TIMING_TOLERANCE):
        self.leading_time = 9000
        self.new_pause_time = 4500
        self.repeat_pause_time = 2250
        self.low_time = 562.5
        self.new_frame_pulses = 67
        self.repeat_frame_pulses = 3
        self.first_data_bit_index = 2
        self.new_message_bits = self.new_frame_pulses - self.first_data_bit_index
        self.timing_tolerance = time_tolerance
        self.extended_protocol = extended_protocol
        self.current_message_type = None
        self.last_code = None

    def _find_start_index(self, pulses: list) -> int:
        """
        Find the start of the frame.

        Args:
            pulses: A list where each element is the time between pulses

        Returns:
            The index for the start of the frame if valid else INVALID_FRAME
        """

        for index, element in enumerate(pulses):
            if abs(self.leading_time -
                   element) < self.leading_time * self.timing_tolerance:
                return index

        return INVALID_FRAME

    def _classify_message(self, pulses: list, start_index: int):
        """
        Sets current_message_type by looking at the pause after the ACG break

        Args:
            pulses: A list where each element is the time between pulses
            start_index: The index of the start pulse (AGC burst and start of frame)

        """

        if abs(pulses[start_index + 1] - self.new_pause_time
               ) < self.timing_tolerance * self.new_pause_time:
            self.current_message_type = NEW_MESSAGE
        elif abs(pulses[start_index + 1] - self.repeat_pause_time
                 ) < self.timing_tolerance * self.new_pause_time:
            self.current_message_type = REPEAT_MESSAGE
        else:
            self.current_message_type = INVALID_FRAME

    def _validate_pulses(self, pulses: list, start_index: int) -> bool:
        """
        Validate the list of pulse times.
        In order for a pulse to be valid there has to be:
        - At least 67 total pulses
        - A start burst followed by a pause
        - A low bit at the end

        Presence of start burst is not tested because it will have already been checked in _find_start_index.

        Args:
            pulses: A list where each element is the time between pulses
            start_index: The index of the start pulse (AGC burst and start of frame)

        Returns:
            True if the pulses are valid and False if not.
            Note that this does not determine if the frame itself is valid
        """

        if self.current_message_type == NEW_MESSAGE:
            if len(pulses) >= self.new_frame_pulses:

                # Second pulse is a pause
                if abs(self.new_pause_time - pulses[start_index + 1]
                       ) < self.new_pause_time * self.timing_tolerance:

                    # Ending pulse is low
                    if abs(self.low_time - pulses[self.new_frame_pulses - 1]
                           ) < self.low_time * self.timing_tolerance:
                        return True

        elif self.current_message_type == REPEAT_MESSAGE:
            if len(pulses) >= self.repeat_frame_pulses:

                # Second pulse is a pause
                if abs(self.repeat_pause_time - pulses[start_index + 1]
                       ) < self.repeat_pause_time * self.timing_tolerance:

                    # Ending pulse is low
                    if abs(self.low_time - pulses[self.repeat_frame_pulses - 1]
                           ) < self.low_time * self.timing_tolerance:
                        return True

        return False

    def _convert_pulses(self, pulses: list, start_index: int) -> list:
        """
        Convert a list of pulse timings to a bit list describing the frame

        Args:
            pulses: A list of valid pulse timings
            start_index: The index of the first bit (the AGC burst)

        Returns:
            A list of numbers which is the binary representation of the address and command
        """

        # Pulses come in pairs of either short, short or short, long so we only need to look at every other pulse time
        first_data_bit_index = start_index + self.first_data_bit_index + 1
        data_bits = pulses[first_data_bit_index:first_data_bit_index +
                           self.new_frame_pulses:2]

        return [
            0 if abs(self.low_time - pulse) < self.timing_tolerance *
            self.low_time else 1 for pulse in data_bits
        ]

    def _validate_message(self, message_bits: list) -> bool:
        """
        The NEC spec says the first 8 and second 8 bits of the message should be complements as should the third and
        four 8 bits of the message.

        This is only for non-extended NEC messages.

        Args:
            message_bits: A valid string of bits

        Returns:
            True if the message is valid, False if not
        """

        command = message_bits[16:24]
        command_inverse = message_bits[24:32]

        # Check each bit in the command and return False if any two are not inverses
        if not all(False for bit, bit_inverse in zip(command, command_inverse)
                   if bit == bit_inverse):
            return False

        # Address inverse is only checked for the non-extended protocol
        if not self.extended_protocol:
            address = message_bits[:8]
            address_inverse = message_bits[8:16]

            # Check each bit in the address and return False if any two are not inverses
            if not all(False
                       for bit, bit_inverse in zip(address, address_inverse)
                       if bit == bit_inverse):
                return False

        return True

    def _create_number_from_bits(self, data_bits: list) -> int:
        """
        Create an integer from the list of bits.
        The address is contained in the first 8 or 16 bits (depending on extended protocol)
        and the the command is contained in bits 16-24
        Bits are always sent LSB first so each part of the frame needs be be reversed

        Args:
            data_bits: A list of zeros and ones indicating the number

        Returns:
            code: A hex number where the first part is the address and the second is the command
        """

        command_length = 8
        address_length = 8 if not self.extended_protocol else 16

        address = 0
        for bit in reversed(data_bits[:address_length:]):
            address = (address << 1) | bit

        # Shift the address over to make room for the command
        address <<= command_length

        command = 0
        for bit in reversed(data_bits[16:24:]):
            command = (command << 1) | bit

        return address | command

    def decode(self, pulse_times: list) -> int:
        """
        Given a valid list of pulse times output an integer where the first eight bits are the address and the
        last eight are the command

        Args:
            pulse_times: A list of valid pulse times

        Returns:
            An integer where the first eight bits are the address and the
        """

        start_index = self._find_start_index(pulse_times)
        if start_index != INVALID_FRAME:
            self._classify_message(pulse_times, start_index)

            if self.current_message_type == NEW_MESSAGE:
                if self._validate_pulses(pulse_times, start_index):
                    bits = self._convert_pulses(pulse_times, start_index)
                    if self._validate_message(bits):
                        code = self._create_number_from_bits(bits)
                        self.last_code = code
                        return code

            # Repeat messages are not validated
            else:
                return self.last_code

        return INVALID_FRAME
