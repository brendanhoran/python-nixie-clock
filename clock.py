#!/usr/bin/python

# Serial port access: Serial is for Linux, machine is for MicroPython
try:
    import serial
except ImportError:
    from machine import UART, RTC

# Requests: What requests module to use, urequests is for Micropython only
try:
    import requests
except ImportError:
    import urequests

import json
import time
from datetime import date, datetime


class UnknownDevice(Exception):
    pass


class SerialWrite:
    ''' Handle all the UART or serial connection and writing tasks '''
    def __init__(self, serial_port):
        # Select what platform we are running on
        if serial_port == 'micropython':
            self.setup_uart()
            self.device_type = 'micropython'
        else:
            self.setup_serial(serial_port)
            self.device_type = 'pc'

    def setup_serial(self, serial_port):
        ''' Setup a serial port for other Python platforms '''
        self.serial_write = serial.Serial()
        self.serial_write.baudrate = 9600
        self.serial_write.timeout = 1
        self.serial_write.port = serial_port

    def setup_uart(self):
        ''' Setup the UART for Micropython platforms '''
        uart = UART(1, 9600, timeout=0)
        uart.init(9600, bits=8, parity=None, stop=1, rx=25, tx=26)
        self.serial_write = uart

    def write_data(self, data):
        ''' Write the data to the serial port or UART '''
        if self.device_type == 'micropython':
            # Write to UART
            data += '\r\n'
            self.serial_write.write(data.encode())
        else:
            try:
                # Write to serial port device
                self.serial_write.open()
                if self.serial_write:
                    data += '\r\n'
                    self.serial_write.write(data.encode())
                    self.serial_write.close()
            except FileNotFoundError:
                print('FileNotFoundError')


class Esp32Rtc:
    ''' Functions that handle setting the RTC and returning time and date '''
    def __init__(self):
        self.rtc = RTC()

    def set_rtc(self,time_format):
        ''' Set the time and date on the RTC '''
        # RTC is not timezone aware, so just set it to the users localtime
        # REF:
        # https://forum.micropython.org/viewtopic.php?f=18&t=10596&p=58464&hilit=rtc#p58464

        # Value returned looks like : 2020-05-13T21:44:36.732570+08:00
        time_data = urequests.get('http://worldtimeapi.org/api/ip')
        date_time = json.loads(time_data.text)

        # Pull out the sections we care about from the JSON string
        date_time = (date_time['datetime'])
        year = int(date_time[0:4])
        month = int(date_time[5:7])
        day = int(date_time[8:10])
        hour = int(date_time[11:13])

        # 12/24 hour conveter, when running tin 12h mode will convert the native 24h time back to 12h time
        # In order to keep date time string consistence, a leading zero is inserted.
        if time_format == '12h':
            hour = int(date_time[11:13])
            hours_in_24h_time = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
            if hour in hours_in_24h_time:
                hour = hour - 12
                # Micropython lacks the ".format()" function.
                hour = int(("%02d" % (hour,)))
  
        minute = int(date_time[14:16])
        second = int(date_time[17:19])

        # Set the esp32's RTC based on the data we get from the REST call above
        # Format for the RTC is:
        # (year, month, day, weekday, hours, minutes, seconds, subseconds)
        # Set the day of the week to 0 as we do not use this value
        # Set microsecond to 00 as we do not need that level of precision
        # Set Timezone to 00 as its not functional in the ESP32.
        self.rtc.init((year, month, day, 00, hour, minute, second, 00))

    def get_rtc(self):
        ''' Get the time and date based on the adjusted UTC '''
        # This returns the date and time based on the users Timezone
        rtc_datetime = self.rtc.datetime()
        # Store as strings so we can concatenate them later
        year = str(rtc_datetime[0])
    
        # Zero pad the following felids to ensure correct formating later on.
        # EG: 6 should be 06 and 10 should be 10.
        # Micropython lacks the ".format()" function.
        month = (rtc_datetime[1])
        month = str(("%02d" % (month,)))

        day = (rtc_datetime[2])
        day = str(("%02d" % (day,)))

        hour = (rtc_datetime[4])
        hour = str(("%02d" % (hour,)))
        
        minute = (rtc_datetime[5])
        minute = str(("%02d" % (minute,)))

        second = (rtc_datetime[6])
        second = str(("%02d" % (second,)))
        
        # concatenate the values 
        rtc_datetime = year+month+day+hour+minute+second
        # return the time in the format we expect
        return rtc_datetime


# class B7Settings:
    # def __init__(self):
        # Not done, maybe won't do
        # idea here is to wrap the tube counting function
        # work out max length for all helper settings

        # do we want all sockets to behave the same
        # if so then set __init__ to work out max length
        # pass


def b7_effect(serial_device, message):
    ''' Set the transition effect type '''
    _command_prefix = '$B7E'
    set_b7_effect = SerialWrite(serial_device)

    set_b7_effect.write_data(_command_prefix+message)


def b7_effect_speed(serial_device, message):
    ''' Set the transition effect speed '''
    _command_prefix = '$B7S'
    set_b7_effect_speed = SerialWrite(serial_device)

    set_b7_effect_speed.write_data(_command_prefix+message)


def b7_font(serial_device, message):
    ''' Set the font to use  on a tube '''
    _command_prefix = '$B7F'
    set_b7_font = SerialWrite(serial_device)

    set_b7_font.write_data(_command_prefix+message)


def b7_message(serial_device, message):
    ''' Write a character to a tube '''
    _command_prefix = '$B7M'
    write_b7_message = SerialWrite(serial_device)

    def _reverse_helper(string):
        """ Ugly helper function since micropython can't split on steps under 1 """
        # https://github.com/micropython/micropython/blob/b9ec6037edf5e6ff6f8f400d70f7351d1b0af67d/py/objstrunicode.c#L189
        reverse = ""
        for character in string:
            reverse = character+reverse
        return reverse

    if serial_device == 'micropython':
        # Use helper to flip the string for MicroPython
        message = _reverse_helper(message)
        write_b7_message.write_data(_command_prefix+message.upper())
    else:
        # Flip the message, socket order is reversed
        message = message[::-1]
        write_b7_message.write_data(_command_prefix+message.upper())


def b7_blank_tube(serial_device, message):
    ''' Blank the tube display, all segments off '''

    # This is not working, only blanks first tube
    # no way to select a tube location

    _command_prefix = '$B7M'
    blank_tube = SerialWrite(serial_device)

    # Space char(ASCII 32) will blank a tube
    blank_tube.write_data(_command_prefix+' ')


def b7_underscore(serial_device, message):
    ''' Set the underscore on or off at a given location '''
    _command_prefix = '$B7U'
    set_b7_underscore = SerialWrite(serial_device)

    set_b7_underscore.write_data(_command_prefix+message)


def get_time_date_data(device, time_format):
    ''' Get the current date and time based on device type '''
    # this section needs a refactor to support the esp32 better

    if device == 'pc':
        # for PC we just read the time from the host machine
        raw_date_time = datetime.datetime.now()
        if time_format == '12h':
            # Format time as YYYYMMDDhhMMSS
            date_time = raw_date_time.strftime('%Y%m%d%I%M%S')
        else:
            # Format time as YYYYMMDDHHMMSS
            date_time = raw_date_time.strftime('%Y%m%d%H%M%S')

        return date_time

    elif device == 'micropython':
        # Get time from the esp32's RTC
        esp32_rtc = Esp32Rtc()
        date_time = esp32_rtc.get_rtc()

        return date_time

    else:
        raise UnknownDevice("Unknown device specified {} : ".format(device))


def format_time(date_time):
    ''' Time selector function, pull only the hours, minutes and seconds from the date_time string '''
    # Select only the HHMMSS from the full date_data object
    date_time = date_time[8::]
    return date_time


def format_date(date_time):
    ''' Date selector function, pull only the year, month and date from the date_time string '''
    # Select only the YYYYMMDD from the full date_data object
    date_time = date_time[:-6]
    return date_time


def display_date_format():   # pragma: no cover
    # not done so ignore coverage tests
    # we should support different ways to display date EG;
    # YYYY MM DD
    # DD MM YYYY
    # MM DD YYYY
    pass


def turn_off_hv_power():    # pragma: no cover
    # not done so ignore coverage tests
    # this should turn off the high voltage power circuit
    # used to safe the life span of the tubes
    # activated from a PIR
    pass


def clear_state(socket_count, serial_device):
    ''' Clear all states in the PIC ensure a known state to start in '''
    # This sets up each smart socket to be in a decent state
    # Sometimes unexpected shutdown causes the PIC to spit crap data
    # A decent state to us is as follows :
    #     1 second transition speed
    #     no active transition pattern
    #     each socket blanked
    socket_count = int(socket_count)
    b7_effect_speed(serial_device, '1' * socket_count)
    b7_effect(serial_device, '0' * socket_count)
    b7_underscore(serial_device, '0' * socket_count)

    # Space char(ASCII 32) sent to all tubes to blank the display
    b7_message(serial_device, ' ' * socket_count)


# def get_date(device_type, time_format):
#     ''' '''
#    raw_date = get_time_date_data(device_type, time_format)
#    date = format_date(raw_date)
#    return date


def display_date(date, seriaL_device):
    ''' Return the full date ready to display '''
    # get the date_data object
    # format the date and display it
    # sleep is needed for serial communications

    time.sleep(1)
    b7_message(seriaL_device, date)
    time.sleep(1)


def read_temp_sensor(serial_device):
    ''' Read external temperature/humidity sensor '''
    # not done #
    time.sleep(1)
    # for now this is a place holder function
    b7_message(serial_device, 'temphu')
    time.sleep(3)


def cathode_poisoning_prevention(socket_count, serial_device):
    ''' Cycle elements in the tube to prevent cathode poisoning '''
    # Format the socket count to be an integer
    socket_count = int(socket_count)
    # set effect speed to 1 second
    b7_effect_speed(serial_device, '1' * socket_count)
    try:
        # Effect type 8, spin full cycle
        b7_effect(serial_device, '8' * socket_count)
        # cycle digits from 0 to 10
        # 0-10 will display numbers 0-9 , up to but not including 10
        for number in range(10):
            number = str(number)
            number = number * socket_count
            b7_message(serial_device, number)
            time.sleep(1)
    except Exception:    # pragma: no cover
        # don't care about errors, move on
        pass
    finally:
        # turn off all transition effects , effect type 0
        b7_effect(serial_device, '0' * socket_count)


def time_action_selector(current_time, socket_count, serial_device, device_type, time_format):
    ''' Main action selector. This constantly parses the time and runs an action when a match is found '''

    # Create some lists that match times that we want to run actions on
    tens = ['10', '20', '30' '40', '50']
    fiftenn_minutes = ['15', '30', '45']
    thirty_minutes = '30'
    on_hour = '59'

    # Every 10 minutes
    if current_time[4::] in tens:
        read_temp_sensor(serial_device)

    # Every 15 minutes
    elif current_time[-4:4] in fiftenn_minutes:
        cathode_poisoning_prevention(socket_count, serial_device)

    # Every 30 minutes
    elif current_time[-4:4] in thirty_minutes:
        display_date(device_type, time_format, serial_device)

    # Once an hour
    elif current_time[-4:4] in on_hour:
        # Not doing anything on the hour yet
        pass
    else:
        b7_message(serial_device, current_time)


class MainSetup:
    ''' Initialize the main clock loop
    Main loop needs the following attributes set when created :
    device_type  -- either PC or esp32 device type
    socket_count -- total amount of smart sockets to use
    time_format -- either 12h or 24h time format
    serial_device -- serial device to use

    '''
    def __init__(self, device_type, socket_count, time_format, serial_device):
        self.device_type = device_type
        self.serial_device = serial_device
        self.socket_count = socket_count
        self.time_format = time_format


class MainLoop(MainSetup):
    ''' This class runs the main clock functions in a endless loop '''

    def main(self):
        ''' The main function sets up any state needed then enters the main endless loop '''
        # On first start up, ensure the smart sockets are in a decent state
        clear_state(self.socket_count, self.serial_device)

        # If we are running on MicroPython, get then store the users time to the RTC.
        if self.device_type == 'micropython':
            esp32_rtc = Esp32Rtc()
            esp32_rtc.set_rtc(self.time_format)

        # Enter loop that runs the main clock functions
        while True:
            get_time = get_time_date_data(self.device_type, self.time_format)
            current_time = format_time(get_time)
            time_action_selector(current_time, self.socket_count, self.serial_device, self.device_type, self.time_format)


if __name__ == "__main__":    # pragma: no cover
    ''' Activated when running on command line from a PC '''
    # Setup the clock  in the following way ;
    #    pc driven mode
    #    6 smart sockets active
    #    24h time format selected
    #    using serial device ttyXRUSB0
    run = MainLoop('pc', '6', '24h', '/dev/ttyXRUSB0')
    run.main()
