# Building MicroPython For LilyGo-TTGO
This is a tutorial for running Green Tech Lab's MySense on the LilyGo-TTGO board.

If another board is desired to be used which hasn't been ported, have a look at their porting tutorial [here](https://github.com/micropython/micropython/tree/master/ports/esp32#defining-a-custom-esp32-board).

---
Note: The log level has been altered as a hotfix for compatibilty with any non-LoPy board. The changed loglevel is found in `mysense/core/logger.py`, `Fatal` and `Error` are changed to a loglevel of 2, this prevents a call to LoPy's library for non-volatile storage (retain written to data despite reboot). 
---

# Prerequisites
## Setup Espressif ESP-IDF

Espressif IDF is used to build a MicroPython environment for the MySense software to run in.

1. Determine the required esp-idf version compatible with MicroPython:  
Currently MicroPython supports [v4.0.2, v4.1.1, v4.2.2, v4.3.2 and v4.4](https://github.com/micropython/micropython/blob/master/ports/esp32/README.md#:~:text=Currently%20MicroPython%20supports%20v4.0.2%2C%20v4.1.1%2C%20v4.2.2%2C%20v4.3.2%20and%20v4.4), if using another ESP32-[XX] board use [these versions](https://github.com/micropython/micropython/tree/master/ports/esp32#:~:text=ESP32%2DS3%20currently,v4.3.1%20or%20later.) or try out versions yourself from [this table](https://github.com/espressif/esp-idf#esp-idf-release-and-soc-compatibility) (table __ONLY__ lists esp-idf board compatibility __NOT__ MicroPython compatibility).

2. Setup ESP-IDF:
- For Windows: 

    Download the esp-idf installer [here](https://dl.espressif.com/dl/esp-idf/?idf=4.4), then follow [this installation guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/windows-setup.html) up to and including the chapter: “Using the Command Prompt”. 
    
- On Linux/WSL/Mac: 
    1. Add yourself to the TTY and uucp/dialout group (lookup how to do this for Mac or your Linux distro). 
    2. Follow [the installation guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/linux-macos-setup.html#get-started-prerequisites) up to and including chapter: “Step 4. Set up the environment variables”. 
---
Note: Alternatively, an IDE extension is available yet DOES NOT include the required `idf.py` used for building MicroPython. You can obtain the extension here for [VSCode](https://github.com/espressif/vscode-esp-idf-extension/blob/master/docs/tutorial/install.md) (aka Chromium) or [Eclipse](https://github.com/espressif/idf-eclipse-plugin/blob/master/README.md). The same is true for the Python package `esptool`.
---

## Setup Uploading Code
To upload code the python package _ampy_ is used.

Activate the newly created espressif/esp-idf Python virtual environment.  
__OR__ Create a new virtual environment and activate it:  
`$ python -m venv ampy_venv`

On Linux/Mac:
`$ . ./ampy_venv/bin/activate`

For Windows:
- Command promt 
`$ ampy_venv\Scripts\activate.bat`
- PowerShell: 
`$ ampy_venv\Scripts\activate.ps1`

Now install “adafruit-ampy" which is used later on to upload the MySense Python code to the board: 

`$ python –m pip install adafruit-ampy`

## Setup Monitoring Board Output

`$ python –m pip install picocom`



# Build Instructions

MicroPython is built from source because the MySense software does not fit in the RAM of the TTGO, therefore the Python modules are compiled into bytecode and included in the MicroPython image, this whole image is then flashed on the TTGO.

1. Clone the MicroPython repository with its submodules: 

    `$ git clone “https://github.com/micropython/micropython“ --recursive` 

2. Build the files required for building the desired board:

    `$ make -C mpy-cross`

3. `$ cd ports/esp32/boards/`
4. `$ make submodules`
5. Freezing the modules:

    Copy the directory `MySense/modules` into: `micropython/ports/esp32/boards/LILYGO_TTGO_LORA32/modules`
--- 
Note: Yes not a typo, “modules/modules”! 
---
This step needs to be redone each time changes to the MySense code are made.

Alternatively, to freeze modules into a more sane directory name, create a new directory inside `LILYGO_TTGO_LORA32`, then add its name to the freeze list located in `LILYGO_TTGO_LORA32/manifest.py`. 

6. In the frozen modules directory (`modules/modules`) create an empty file called `__init__.py`.
7. Finally build the board image: 

    `$ make BOARD=LILYGO-TTGO-LORA32`



# Flashing MicroPython Instructions

Now everything should be ready for running the code on the board.

1. Connect the board to your PC using a USB cable.

2. __Every time a new flash is performed__ it is advised to erase the currently flashed image:
    `$ esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash`
---
Note: On Windows change `--port /dev/ttyUSB0` with `--port COM[X]` where `[X]` is replaced with the board's COM number. Find out in Device Manager under the Ports category which COM port the board is using.
---
---
On MacOS the device is likely to start with `/dev/cu.[device_name]`
---
3. Now upload the firmware, if after building MicroPython you got a different command to the one below, use it instead. Also be sure to replace the port in the command below:

    `$ esptool.py -p [PORT /dev/ttyUSB0 OR COM[X]] -b 460800 --before default_reset --after hard_reset --chip esp32  write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 build-LILYGO_TTGO_LORA32/bootloader/bootloader.bin 0x8000 build-LILYGO_TTGO_LORA32/partition_table/partition-table.bin 0x10000 build-LILYGO_TTGO_LORA32/micropython.bin`



# Uploading MySense

Two MicroPython files are present on the board by default:
- main.py   Runs on a loop.
- boot.py:  Runs once on boot.

Copy MySense's `main.py` to `boot.py`. This assumes you're in the LilyGo branch if not, in the file `main.py` you should change `import MySense` to `import mysense.MySense`.

Use the `ampy` virtual environment to copy the essential MySense files over, this will take some time:
```
ampy -p /dev/ttyUSB0 put boot.py && \
ampy -p /dev/ttyUSB0 put config && \
ampy -p /dev/ttyUSB0 put core && \
ampy -p /dev/ttyUSB0 put main.py && \
ampy -p /dev/ttyUSB0 put MySense.py && \
echo "Finished Uploading"
```
MySense lists the modules directory to load in the modules, we froze these modules, thus they cannot be found by MySense. For MySense to find these modules, create a modules directory using `ampy` and __for each__ module create an __empty__ file with the same name and directory structure. The files need be empty to prevent these unoptimized/unfrozen files being loaded into RAM, which doesn't fit.

# Running MySense

Run `$ picocom [port] -b 115200` to monitor the board's output. You may need to press the board's reset button or disconnect and reconnect the USB cable followed by the picocom command to catch the output at the start.