#!/usr/bin/python


import serial
import json
import requests
import time
import datetime

class SerialWrite:
    def __init__(self, serial_port):

        self.serial_write = serial.Serial()
        self.serial_write.baudrate = 9600
        self.serial_write.timeout = 1
        self.serial_write.port = serial_port
    
    def write_data(self, data):
        self.serial_write.open()
        if self.serial_write:
            data += '\r\n'
            self.serial_write.write(data.encode())
            self.serial_write.close()


class Esp32Rtc:
    def __int__(self):
        self.rtc = machine.RTC()

    def set_rtc(self,date_time):
        time_data = requests.get('http://worldtimeapi.org/api/ip')
        date_time = json.loads(time_data.text)
    
        #  value returned looks like : 2020-05-13T21:44:36.732570+08:00
        date_time = (date_time['datetime'])
        year = date_time[0:4]
        month = date_time[5:7]
        day = date_time[8:10]
        hour = date_time[11:13]
        minute = date_time[14:16]
        second = date_time[17:19]
        tz = date_time[26:29]

        self.rtc.init((year, month, day, hour, minute, second, tz))

    def get_rtc(self):
        rtc_date_time = self.rtc.datetime()
        year = rtc_date_time[0]
        month = rtc_date_time[1]
        day = rtc_date_time[2]
        hour = rtc_date_time[3]
        minute = rtc_date_time[4]
        second = rtc_date_time[5]

        return year+month+day+hour+minute+second

class B7Settings:
    def __init__(self):
        # idea here is to wrap the tube counting function
        # work out max length for all helper settings

        # do we want all sockets to behave the same
        # if so then set __init__ to work out max length 
        pass


def b7_effect(serial_device,message):
    _command_prefix = '$B7E'
    set_b7_effect = SerialWrite(serial_device)

    set_b7_effect.write_data(_command_prefix+message)

def b7_effect_speed(serial_device,message):
    _command_prefix = '$B7S'
    set_b7_effect_speed = SerialWrite(serial_device)

    set_b7_effect_speed.write_data(_command_prefix+message)

def b7_font(serial_device,message):
    _command_prefix = '$B7F'
    set_b7_font = SerialWrite(serial_device)

    set_b7_font.write_data(_command_prefix+message)

def b7_message(serial_device,message):
    _command_prefix = '$B7M'
    write_b7_message = SerialWrite(serial_device)

    # Flip the message, socket order is reversed
    message = message[::-1]
    write_b7_message.write_data(_command_prefix+message.upper())

def b7_blank_tube(serial_device, tube_id):
   ''' not done yet '''
   _command_prefix = '$B7M'
   blank_tube = SerialWrite(serial_device)

   # Space char(ASCII 32) will blank a tube
   blank_tube.write_data(_command_prefix+' ')

def b7_underscore(serial_device,message):
    _command_prefix ='$B7U'
    set_b7_underscore = SerialWrite(serial_device)

    set_b7_underscore.write_data(_command_prefix+message)

def get_time_data_data(device):
    
    if device == 'pc':
        raw_date_time = datetime.datetime.now()
        # Format time as YYYYMMDDHHMMSS
        date_time = raw_date_time.strftime('%Y%m%d%H%M%S')

        return date_time
    
    elif device == 'esp32':
        date_time = Esp32Rtc.get_rtc()
    else:
        # make this nicer, exception etc...
        print('unknown device')

def format_time(date_time):
    date_time = date_time[8::]
    return date_time

def format_date(date_time):
    date_time = date_time[:-6]
    return date_time

def hours_24_to_12():
    pass


class MainSetup:
    def __init__(self, device_type, socket_count, serial_device):
        self.device_type = device_type
        self.serial_device = serial_device
        self.socket_count = socket_count


class MainLoop(MainSetup):
    def main(self):
        while True:
            get_time = get_time_data_data(self.device_type)
            current_time = format_time(get_time)
            print(current_time)
            if current_time[4::] == '10':
                self.read_temp_sensor()
            elif current_time[2::] == '1500':
                self.cathode_poisoning_prevention(6)
            elif current_time[2::] == '4800':
                self.display_date()
            else:
                b7_message(self.serial_device, current_time)

    def read_temp_sensor(self):
        time.sleep(1)
        b7_message(self.serial_device, 'temphu')
        time.sleep(3)


    def display_date(self):
        raw_date = get_time_data_data(self.device_type)
        date = format_date(raw_date)
        time.sleep(1)
        b7_message(self.serial_device, date)
        time.sleep(1)


    def cathode_poisoning_prevention(self):
        # set effect speed to 1 second
        b7_effect_speed('/dev/ttyUSB0', '1' * self.socket_count)
        try:
            # Effect type 8, spin full cycle
            b7_effect('/dev/ttyUSB0', '8' * self.socket_count)
            # cycle digits from 0 to 10
            for number in range(10):
                number = str(number)
                number = number * self.socket_count
                b7_message(self.serial_device, number)
                time.sleep(1)
        except Exception as error:
            # don't care about errors, move on
            print('error in effect loop : {}'.format(error))
        finally:
            # turn off all transition effects , effect type 0 
            b7_effect('/dev/ttyUSB0', '0'* self.socket_count)


if __name__ == "__main__":

    run = MainLoop('pc', '6', '/dev/ttyUSB0')
    run.main()
    