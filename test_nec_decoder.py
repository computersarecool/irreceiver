from unittest import TestCase

from nec_decoder import NecDecoder, INVALID_FRAME, REPEAT_MESSAGE, NEW_MESSAGE


class TestNecDecoder(TestCase):
    # This is a tolerance which prohibits any two pulse times from overlapping
    time_multiplier = .3

    # Most tests are run against the frame for address 00h (00000000b) and command ADh (10101101b):
    reference_pulses = [
        # Pulse and space
        9000,
        4500,
        # Address pt 1
        562.5,
        562.5,
        562.5,
        562.5,
        562.5,
        562.5,
        562.5,
        562.5,
        # Address pt 2
        562.5,
        562.5,
        562.5,
        562.5,
        562.5,
        562.5,
        562.5,
        562.5,
        # Address inverse pt 1
        562.5,
        1687.5,
        562.5,
        1687.5,
        562.5,
        1687.5,
        562.5,
        1687.5,
        # Address inverse pt 2
        562.5,
        1687.5,
        562.5,
        1687.5,
        562.5,
        1687.5,
        562.5,
        1687.5,
        # Command (LSB first) pt 1
        562.5,
        1687.5,
        562.5,
        562.5,
        562.5,
        1687.5,
        562.5,
        1687.5,
        # Command (LSB first) pt 2
        562.5,
        562.5,
        562.5,
        1687.5,
        562.5,
        562.5,
        562.5,
        1687.5,
        # Command (LSB first) inverse pt 1
        562.5,
        562.5,
        562.5,
        1687.5,
        562.5,
        562.5,
        562.5,
        562.5,
        # Command (LSB first) inverse pt 2
        562.5,
        1687.5,
        562.5,
        562.5,
        562.5,
        1687.5,
        562.5,
        562.5,
        # Final burst
        562.5
    ]

    # The reference_pulses correspond to this list of bits
    reference_bits = [
        0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1,
        0, 1, 0, 0, 1, 0, 1, 0
    ]

    # Which corresponds to 173 or 0x00AD in hex
    reference_number = 0x00AD

    # Pause, pulse space and low
    reference_repeat_pulses = [9000, 2250, 562.5]

    # Finding start of frame
    def test__find_start_index_spec(self):
        decoder = NecDecoder()
        first_element_index = 0
        start = decoder._find_start_index(TestNecDecoder.reference_pulses)

        assert start == first_element_index

    def test__find_start_index_slow(self):
        pulses_slow = [
            pulse + pulse * TestNecDecoder.time_multiplier
            for pulse in TestNecDecoder.reference_pulses
        ]

        decoder = NecDecoder()
        first_element_index = 0
        start = decoder._find_start_index(pulses_slow)

        assert start == first_element_index

    def test__find_start_index_fast(self):
        pulses_fast = [
            pulse - pulse * TestNecDecoder.time_multiplier
            for pulse in TestNecDecoder.reference_pulses
        ]

        decoder = NecDecoder()
        first_element_index = 0
        start = decoder._find_start_index(pulses_fast)

        assert start == first_element_index

    def test__find_start_index_no_start(self):
        reference_pulses_no_start = TestNecDecoder.reference_pulses[1:]

        decoder = NecDecoder()
        start = decoder._find_start_index(reference_pulses_no_start)

        assert start == INVALID_FRAME

    # Classify message
    def test_new_message(self):
        decoder = NecDecoder()
        start = decoder._find_start_index(TestNecDecoder.reference_pulses)

        decoder._classify_message(TestNecDecoder.reference_pulses, start)

        assert decoder.current_message_type == NEW_MESSAGE

    def test_repeat_message(self):
        decoder = NecDecoder()
        start = decoder._find_start_index(
            TestNecDecoder.reference_repeat_pulses)

        decoder._classify_message(TestNecDecoder.reference_repeat_pulses,
                                  start)

        assert decoder.current_message_type == REPEAT_MESSAGE

    # Valid pulses
    def test_valid_pulses(self):
        decoder = NecDecoder()
        start = decoder._find_start_index(TestNecDecoder.reference_pulses)
        decoder._classify_message(TestNecDecoder.reference_pulses, start)

        assert decoder._validate_pulses(TestNecDecoder.reference_pulses, start)

    def test_invalid_pulse_length(self):
        reference_pulses_not_enough = TestNecDecoder.reference_pulses[:-1]

        decoder = NecDecoder()
        start = decoder._find_start_index(reference_pulses_not_enough)

        assert not decoder._validate_pulses(reference_pulses_not_enough, start)

    def test_no_pause(self):
        # Set the pause to a low time
        reference_pulses = TestNecDecoder.reference_pulses[:]
        reference_pulses[1] = 562.5
        reference_pulses_no_pause = reference_pulses

        decoder = NecDecoder()
        start = decoder._find_start_index(reference_pulses_no_pause)

        assert not decoder._validate_pulses(reference_pulses_no_pause, start)

    def test_no_end_low(self):
        # Set the last pulse to a high time
        reference_pulses = TestNecDecoder.reference_pulses[:]
        reference_pulses[len(reference_pulses) - 1] = 1687.5
        reference_pulses_no_end_low = reference_pulses

        decoder = NecDecoder()
        start = decoder._find_start_index(reference_pulses_no_end_low)

        assert not decoder._validate_pulses(reference_pulses_no_end_low, start)

    # Convert pulses to a list of bits
    def test_convert_pulses_valid(self):
        decoder = NecDecoder()
        start = decoder._find_start_index(TestNecDecoder.reference_pulses)

        assert TestNecDecoder.reference_bits == decoder._convert_pulses(
            TestNecDecoder.reference_pulses, start)

    def test_convert_pulses_slow(self):
        pulses_slow = [
            pulse + pulse * TestNecDecoder.time_multiplier
            for pulse in TestNecDecoder.reference_pulses
        ]

        decoder = NecDecoder()
        start = decoder._find_start_index(TestNecDecoder.reference_pulses)

        assert TestNecDecoder.reference_bits == decoder._convert_pulses(
            pulses_slow, start)

    def test_convert_pulses_fast(self):
        pulses_fast = [
            pulse - pulse * TestNecDecoder.time_multiplier
            for pulse in TestNecDecoder.reference_pulses
        ]

        decoder = NecDecoder()
        start = decoder._find_start_index(TestNecDecoder.reference_pulses)

        assert TestNecDecoder.reference_bits == decoder._convert_pulses(
            pulses_fast, start)

    # Valid bit lists
    def test__validate_message_valid(self):
        decoder = NecDecoder()

        assert decoder._validate_message(TestNecDecoder.reference_bits)

    def test__validate_message_invalid(self):
        # Flip the first bit
        bit_list_valid = TestNecDecoder.reference_bits[:]
        bit_list_valid[0] = 1 - bit_list_valid[0]
        bit_list_invalid = bit_list_valid

        decoder = NecDecoder()

        assert not decoder._validate_message(bit_list_invalid)

    def test__create_number_from_bits_spec(self):
        decoder = NecDecoder()

        assert decoder._create_number_from_bits(
            TestNecDecoder.reference_bits) == TestNecDecoder.reference_number

    def test__create_number_from_bits_with_address(self):
        # The spec bit_list looks like:
        # bit_list_with_address = [
        #     0, 0, 0, 0, 0, 0, 0, 0,
        #     1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 0, 1, 1, 0, 1, 0, 1,
        #     0, 1, 0, 0, 1, 0, 1, 0
        # ]
        # Which has no address
        # The following adds an address of one, which checks that the LSB is being set first
        # That will create an address of 1 and the same message value of 173
        # Must remember to flip the corresponding bit in the inverse byte

        address = 1
        command = 173

        bit_list_with_address = TestNecDecoder.reference_bits[:]
        bit_list_with_address[0] = 1
        bit_list_with_address[8] = 0

        decoder = NecDecoder()
        number_returned = decoder._create_number_from_bits(
            bit_list_with_address)

        input_command = address << 8 | command

        assert number_returned == input_command

    def test_decode_spec(self):
        decoder = NecDecoder()

        assert decoder.decode(
            TestNecDecoder.reference_pulses) == TestNecDecoder.reference_number

    def test_decode_spec_slow(self):
        pulses_slow = [
            pulse + pulse * TestNecDecoder.time_multiplier
            for pulse in TestNecDecoder.reference_pulses
        ]

        decoder = NecDecoder()

        assert decoder.decode(pulses_slow) == TestNecDecoder.reference_number

    def test_decode_spec_fast(self):
        pulses_slow = [
            pulse - pulse * TestNecDecoder.time_multiplier
            for pulse in TestNecDecoder.reference_pulses
        ]

        decoder = NecDecoder()

        assert decoder.decode(pulses_slow) == TestNecDecoder.reference_number

    def test_decode_spec_extended(self):
        # The address is now 49153 and not inverted
        # The command is the same 173
        # In bits this would look like:
        # bit_list_with_address = [
        #     1, 0, 0, 0, 0, 0, 0, 0,
        #     0, 0, 0, 0, 0, 0, 1, 1,
        #     1, 0, 1, 1, 0, 1, 0, 1,
        #     0, 1, 0, 0, 1, 0, 1, 0
        # ]

        reference_pulses_extended = [
            # Pulse and space
            9000,
            4500,
            # Address pt 1
            562.5,
            1687.5,
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            # Address pt 2
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            # Address pt 3
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            # Address pt 4
            562.5,
            562.5,
            562.5,
            562.5,
            562.5,
            1687.5,
            562.5,
            1687.5,
            # Command (LSB first) pt 1
            562.5,
            1687.5,
            562.5,
            562.5,
            562.5,
            1687.5,
            562.5,
            1687.5,
            # Command (LSB first) pt 2
            562.5,
            562.5,
            562.5,
            1687.5,
            562.5,
            562.5,
            562.5,
            1687.5,
            # Command (LSB first) inverse pt 1
            562.5,
            562.5,
            562.5,
            1687.5,
            562.5,
            562.5,
            562.5,
            562.5,
            # Command (LSB first) inverse pt 2
            562.5,
            1687.5,
            562.5,
            562.5,
            562.5,
            1687.5,
            562.5,
            562.5,
            # Final burst
            562.5
        ]

        reference_pulses_extended_number = 0xC001AD

        decoder = NecDecoder(True)
        return_code = decoder.decode(reference_pulses_extended)

        assert return_code == reference_pulses_extended_number

    def test_decode_repeat_spec(self):
        # Create a decoder and "send" a frame
        decoder = NecDecoder()
        code = decoder.decode(TestNecDecoder.reference_pulses)

        repeat_response = decoder.decode(
            TestNecDecoder.reference_repeat_pulses)

        assert code == repeat_response

    def test_decode_repeat_spec_slow(self):
        decoder = NecDecoder()
        code = decoder.decode(TestNecDecoder.reference_pulses)

        repeat_command_slow = [
            pulse + pulse * TestNecDecoder.time_multiplier
            for pulse in TestNecDecoder.reference_repeat_pulses
        ]

        repeat_response = decoder.decode(repeat_command_slow)

        assert code == repeat_response

    def test_decode_repeat_spec_fast(self):
        decoder = NecDecoder()
        code = decoder.decode(TestNecDecoder.reference_pulses)

        repeat_command_fast = [
            pulse + pulse * TestNecDecoder.time_multiplier
            for pulse in TestNecDecoder.reference_repeat_pulses
        ]

        repeat_response = decoder.decode(repeat_command_fast)

        assert code == repeat_response
