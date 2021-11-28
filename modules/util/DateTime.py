# The calendar is only used in PC mode
try:
    import calendar
except ImportError:
    pass

import time
from vendor.datetime import date, datetime
from drivers import SmartSocket
from util import EspRtc

class UnknownDevice(Exception):
    pass


def get_time_date_data(device, time_format):
    ''' Get the current date and time based on device type '''

    if device == 'pc':
        # for PC we just read the time from the host machine
        raw_date_time = datetime.now()
        if time_format == '12h':
            # Format time as YYYYMMDDhhMMSS
            date_time = raw_date_time.strftime('%Y%m%d%I%M%S')
        else:
            # Format time as YYYYMMDDHHMMSS
            date_time = raw_date_time.strftime('%Y%m%d%H%M%S')

        return date_time

    elif device == 'micropython':
        # Get time from the esp32's RTC
        esp32_rtc = EspRtc.Esp32Rtc()
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


def display_date_format(device_type, time_format, date_format):
    ''' Format the date based on users preference '''
    date = get_date(device_type, time_format)
    year = date[:-4]
    month = date[4:-2]
    day = date[6:]
    short_year = date[2:-4]
    
    # Format date for DDMMYY
    if date_format == 'DDMMYY':
        date = day + month + short_year
        return date

    # Format date for MMDDYY
    elif date_format == 'MMDDYY':
        date = month + day + short_year 
        return date

    # format date for YYMMDD
    elif date_format == 'YYMMDD':
        date = short_year + month + day
        return date

    # format date for DDMMYYYY
    elif date_format == 'DDMMYYYY':
        date = day + month + year
        return date

    # Format date for MMDDYYYY
    elif date_format == 'MMDDYYYY':
        date = month + day + year
        return date
        
    # Else return the default of YYYYMMDD
    else:
        return date

def get_date(device_type, time_format):
    ''' Get date based on device type and return in the format of: YYYYMMDDH '''
    raw_date = get_time_date_data(device_type, time_format)
    date = format_date(raw_date)
    return date


def display_date(device_type, serial_device, time_format, date_format):
    ''' Display date on smart socket '''
    date = display_date_format(device_type, time_format, date_format)
    print(date)
    time.sleep(1)
    SmartSocket.b7_message(serial_device, date)
    time.sleep(1)


def write_day_as_word(serial_device):
    if serial_device == 'pc':
        todays_date = date.today()
        weekday_name = calendar.day_name[todays_date.weekday()]
        SmartSocket.b7_message(serial_device, weekday_name)
    
    elif serial_device == 'micropython':
        # Micropython has no enum support so use a dict to map number to name of the day
        _day_mapping ={
            '0': 'Sunday',
            '1': 'Monday',
            '2': 'Tuesday',
            '3': 'Wednesday',
            '4': 'Thursday',
            '5': 'Friday',
            '6': 'Saturday' 
        }

        esp32_rtc = EspRtc.Esp32Rtc()
        day_number  = esp32_rtc.get_day_number()
        weekday_name = _day_mapping[day_number]
        SmartSocket.b7_message(serial_device, weekday_name)
    else:
        # If we don't match its most likely not a smart socket device
        pass
