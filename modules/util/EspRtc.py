try:
    from machine import RTC
except ImportError:
    pass

# Requests: What requests module to use, urequests is for Micropython only
try:
    import requests
except ImportError:
    import urequests

import json

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
        time_date_request_data = urequests.get('http://worldtimeapi.org/api/ip')
        time_date_data = json.loads(time_date_request_data.text)

        # Pull out the sections we care about from the JSON string
        day_number = (time_date_data['day_of_week'])
        
        date_time = (time_date_data['datetime'])
        year = int(date_time[0:4])
        month = int(date_time[5:7])
        day = int(date_time[8:10])
        hour = int(date_time[11:13])
 

        # 12/24 hour conveter, when running in 12h mode will convert the native 24h time back to 12h time
        # In order to keep date time string consistence, a leading zero is inserted.
        if time_format == '12h':
            hour = int(date_time[11:13])
            hours_in_24h_time = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
            if hour in hours_in_24h_time:
                hour = hour - 12
                # Micropython lacks the ".format()" function.
                hour = str(("%02d" % (hour,)))
                hour = int(hour)
  
        minute = int(date_time[14:16])
        second = int(date_time[17:19])

        # Set the esp32's RTC based on the data we get from the REST call above
        # Format for the RTC is:
        # (year, month, day, weekday, hours, minutes, seconds, subseconds)
        # Set microsecond to 00 as we do not need that level of precision
        # Don't set a Timezone to as its not functional in the ESP32.
        self.rtc.init((year, month, day, day_number, hour, minute, second, 00))

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

    def get_day_number(self):
        ''' Get the day number  from the RTC '''
        rtc_datetime = self.rtc.datetime()
        day_number = (rtc_datetime[3])
