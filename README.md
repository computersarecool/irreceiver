# IRReceiver
*A Python Package to parse the NEC IR remote control protocol*

## Description
This is a fully tested Python package to parse the NEC IR remote control protocol.

The NEC protocol is used by many remotes, you can read about it [here](https://www.sbprojects.net/knowledge/ir/nec.php).

**NOTE: Although there is an example of this sketch that is made for the Raspberry PI, it is unlikely to work. 
The Raspberry Pi does [not have a real time operating system](https://www.socallinuxexpo.org/sites/default/files/presentations/Steven_Doran_SCALE_13x.pdf)
and in my testing this did not work reliably.**

## Dependencies
- This project has no external dependencies but the example code does depend on being run on a Raspberry Pi.
- All code follows PEP 8 and there is a Github action to run code through [YAPF](https://github.com/google/yapf) before it is merged to the main branch.

## Tested On
- A Raspberry Pi (first generation)
- A Yamaha MRX-90M remote

## To Install
- `pip install irreceiver`


## To Use
- An example file can be found in the `examples` directory.
- Here is a basic example of decoding an list of IR timing pulses:
```python
from irreceiver import NecDecoder
decoder = NecDecoder()
# PULSES should be a list of IR pulse timings
message = decoder.decode(PULSES)
# Message will be a number such as 0x00AD where the first byte 00 is the address and the second byte AD is the command 
```

## Project Structure
Directory structure should be clear. All code is in the `irreceiver` directory.


### License

:copyright: Willy Nolan 2020

[MIT License](http://en.wikipedia.org/wiki/MIT_License)
