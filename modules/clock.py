#!/usr/bin/python
import time
from drivers import SmartSocket
from util import DateTime
from util import EspRtc


def turn_off_hv_power():    # pragma: no cover
    # not done so ignore coverage tests
    # this should turn off the high voltage power circuit
    # used to save the life span of the tubes
    # activated from a PIR/Mirowave/timer etc 
    pass


def read_temp_sensor(serial_device):
    ''' Read external temperature/humidity sensor '''
    # not done #
    time.sleep(1)
    # for now this is a place holder function
    print('temphu')
    SmartSocket.b7_message(serial_device, 'temphu')
    time.sleep(5)

# This really needs to be refactored later to support normal nixies as well as smart socket
def cathode_poisoning_prevention(socket_count, serial_device):
    ''' Cycle elements in the tube to prevent cathode poisoning '''
    # Format the socket count to be an integer
    socket_count = int(socket_count)
    # set effect speed to 1 second
    SmartSocket.b7_effect_speed(serial_device, ('1' * socket_count))
    try:
        # Effect type 8, spin full cycle
        SmartSocket.b7_effect(serial_device, ('8' * socket_count))
        # cycle digits from 0 to 10
        # 0-10 will display numbers 0-9 , up to but not including 10
        for number in range(10):
            number = str(number)
            number = number * socket_count
            SmartSocket.b7_message(serial_device, number)
            time.sleep(1)
    except Exception:    # pragma: no cover
        # don't care about errors, move on
        pass
    finally:
        print("did we get here, in the try loop for cathode")
        # turn off all transition effects , effect type 0
        SmartSocket.clear_state(socket_count, serial_device)
        time.sleep(1)


def time_action_selector(current_time, socket_count, serial_device, device_type, time_format, date_format):
    ''' Main action selector. This constantly parses the time and runs an action when a match is found '''
    # Match on 00 seconds to ensure functions only get called once per minute
    tens = ['1000', '2000', '4000', '5000']
    fifteen_minutes = ['1500', '4500']
    thirty_minutes = '3000'
    on_hour = '5900'


    # Every 10 minutes, Not in use at the moment
    if current_time[-4:] in tens:
        pass

    # Every 15 minutes read a temperature sensor
    elif current_time[-4:] in fifteen_minutes:
        print('did sensor read')
        read_temp_sensor(serial_device)
    
    # Every 30 minutes display the date
    elif current_time[-4:] in thirty_minutes:
        print('displayed date')
        DateTime.display_date(device_type, serial_device, time_format, date_format)

    # Once an hour run the cothode protection loop
    elif current_time[-4:] in on_hour:
        print('enter cathode protection')
        cathode_poisoning_prevention(socket_count, serial_device)

    # When running on MicroPython, adjust/discipline the RTC once a day
    # This also will auto adjust for DST regions
    # Hence why run this at the users local time of 03:30:00 hrs
    elif device_type == 'micropython' and current_time == '033000':
            print('Adjusted RTC')
            esp32_rtc = EspRtc.Esp32Rtc()
            esp32_rtc.set_rtc(time_format)

    else:
        SmartSocket.b7_message(serial_device, current_time)


class MainSetup:
    ''' Initialize the main clock loop
    Main loop needs the following attributes set when created :
    device_type  -- either PC or esp32 device type
    socket_count -- total amount of smart sockets to use
    time_format -- either 12h or 24h time format
    serial_device -- serial device to use
    date_format -- how to display the date

    '''
    def __init__(self, device_type, socket_count, time_format, date_format, serial_device):
        self.device_type = device_type
        self.serial_device = serial_device
        self.socket_count = socket_count
        self.time_format = time_format
        self.date_format = date_format


class MainLoop(MainSetup):
    ''' This class runs the main clock functions in a endless loop '''

    def main(self):
        ''' The main function sets up any state needed then enters the main endless loop '''
        # On first start up, ensure the smart sockets are in a decent state
        SmartSocket.clear_state(self.socket_count, self.serial_device)

        # If we are running on MicroPython, get and store the users time to the RTC.
        if self.device_type == 'micropython':
            esp32_rtc = EspRtc.Esp32Rtc()
            esp32_rtc.set_rtc(self.time_format)

        # Enter loop that runs the main clock functions
        while True:
            get_time = DateTime.get_time_date_data(self.device_type, self.time_format)
            current_time = DateTime.format_time(get_time)
            time_action_selector(current_time, self.socket_count, self.serial_device, self.device_type, self.time_format, self.date_format)


if __name__ == "__main__":    # pragma: no cover
    ''' Activated when running on command line from a PC '''
    # Setup the clock  in the following way ;
    #    pc driven mode
    #    6 smart sockets active
    #    24h time format selected
    #    Date formfat of Day Month  Year (short)
    #    using serial device ttyXRUSB0
    run = MainLoop('pc', '6', '24h', 'DDMMYY', '/dev/ttyUSB0')
    run.main()
