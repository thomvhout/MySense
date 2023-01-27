# This file is part of the MySense software (https://github.com/MarcoKull/MySense).
# Copyright (c) 2020 Marco Kull
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#from log.print_logger import PrintLogger # default console logger
from core.log import LogLevel

 # for timestamp creation
try:
    import time # python
except:
    import utime as time # micropython

class Logger():
    """
    This is a singleton class to log the application output.
    It also acts as suject for which observers can be added to.
    Creates a print logger by default on creation.
    """

    # implements singleton behaviour by
    # using a private class variable to use for new objects
    __instance = None
    def __new__(cls):
        if Logger.__instance is None:
            # create the singleton object
            Logger.__instance = object.__new__(cls)

            # create list of observers
            Logger.__instance.__observers = [LogPrinter(), NVSLogger()]
            Logger.__instance.__lvl = LogLevel.info

        return Logger.__instance

    def __init__(self):
        pass

    def add(self, observer):
        """Add a LogObserver to be notified on log messages."""
        self.__observers.append(observer)

    def log(self, level, message):
        """Log given message with given level."""

        # log message on all observers
        for o in self.__observers:
            o.log(level, message)

    # log level
    def get_level(self):
        return self.__lvl

    def set_level(self, level):
        self.__observers[0].__lvl = level
        self.__lvl = level

    level = property(get_level, set_level)

    # timestamps
    def get_use_timestamps(self):
        return self.__timestamps

    def set_use_timestamps(self, bool):
        self.__observers[0].use_timestamps = bool
        self.__timestamps = bool

    use_timestamps = property(get_use_timestamps, set_use_timestamps)

class LogObserver():
    """
    Abstract class for log observers.
    The log(level, message) method has to implemented by the child class.
    """

    def __init__(self):
        pass

    def log(self, level, message):
        raise NotImplementedError("The log(level, message) method has to implemented by a LogObserver child class.")

    def ascii_message(level, message, use_timestamps):
        if level == 2:
            l = "Fatal:  "
        elif level == 2:
            l = "Error:  "
        elif level == 2:
            l = "Warning:"
        elif level == 3:
            l = "Info:   "
        elif level == 4:
            l = "Debug:  "
        elif level == 5:
            l = "All:    "
        else:
            l = "UNKNOWN!"

        msg = l + " " + message

        if use_timestamps:
            # create timestamp
            t = utime.localtime() # get time
            ts = ""
            for i in range(0, 6):
                if t[i] < 10: # make sure that timestamp string always has the same size
                    ts += "0"
                ts += str(t[i])
                if i < 2:
                    ts += "/"
                elif i == 2:
                    ts += "-"
                elif i < 5:
                    ts += ":"

            msg = "[" + ts + "] " + msg

        return msg


class LogPrinter(LogObserver):
    """
    Prints log messages with optional timestamps.
    """
    def __init__(self):
        super(LogPrinter, self).__init__()
        self.__lvl = LogLevel.info
        self.__timestamps = False

    def log(self, level, message):
        if self.__lvl >= level:
            print(LogObserver.ascii_message(level, message, self.__timestamps))

    # log level
    def get_level(self):
        return self.__lvl

    def set_level(self, level):
        self.__lvl = level

    level = property(get_level, set_level)

    # timestamps
    def get_use_timestamps(self):
        return self.__timestamps

    def set_use_timestamps(self, bool):
        self.__timestamps = bool

    use_timestamps = property(get_use_timestamps, set_use_timestamps)


class NVSLogger(LogObserver):
    """
    Prints log messages with optional timestamps.
    """
    def __init__(self):
        super(NVSLogger, self).__init__()

    def log(self, level, message):
        if level > 1:
            return

        import pycom
        pycom.nvs_set("elog", message)
