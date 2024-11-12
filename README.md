## CS710S USB Tool for Firmware Updates

This tool allows you to control your reader and perform firmware update with a Linux/Windows/MacOS host

The code is written in Python and tested on x64 desktop (Ubuntu 20.04 LTS) and arm32 (Raspberry Pi 4/Raspbian).

### Dependencies


* [hidapi](https://github.com/libusb/hidapi)

```
$ sudo apt install libhidapi-dev
```

* [pyhidapi](https://github.com/apmorton/pyhidapi)

```
$ pip install hid
```


### Running the Python Scripts

Run the main.py with the firmware file as the argument:

* /B: Bluetooth Firmware
* /N: Network Processor (Atmel) Firmware

```
Usage: python main.py [ /B | /N ] file
```	

Example
```
$ python main.py /B ./FW/CS710_CC2652R7_APP_V1.0.6.bin 
----------------------------
CS710S Firmware Upgrade Toool
----------------------------
Number of USB device(s) connected:  1
Device 0: b'/dev/hidraw0'
Current Atmel processor firmware version: 2.0.6
Current Bluetooth firmware version: 1.0.6

Upgrade Atmel processor firmware with file: ./FW/CS710ATMEL_V2.0.6.bin
Completed:100.0%
>> Wait for 0 seconds
Atmel processor firmware upgrade successful.  Please reboot the reader.
```


