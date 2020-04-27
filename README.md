# IRReceiver
*A module to parse the NEC IR remote control protocol*

## Description
This is a fully tested module that creates a receiver for the NEC IR remote control protocol.

The NEC protocol is used by many remotes, you can read about it [here](https://www.sbprojects.net/knowledge/ir/nec.php).

## Dependencies
- This project has no external dependencies but the example code does depend on a Raspberry Pi.

## Tested On
- A Raspberry Pi (first generation)
- A Yamaha MRX-90M remote

## To Build
- Just include the file

## To Use
- Look at the file `nec_example.py`. Essentially just call `decode` on an instance of `NecDecoder` 

## Project Structure
All files in root


### License

:copyright: Willy Nolan 2020

[MIT License](http://en.wikipedia.org/wiki/MIT_License)
