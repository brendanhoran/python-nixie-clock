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
        self.rtc.datetime(date_time)

    def get_rtc(self):
        rtc_date_time = self.rtc.datetime()
        return rtc_date_time

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
   blank_tube = SerialWrite(serial_device)

   # Space char(ASCII 32) will blank a tube
   blank_tube.write_data(' ')

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
        time_data = requests.get('http://worldtimeapi.org/api/ip')
        date_time = json.loads(time_data.text)
    
        #  value returned looks like : 2020-05-13T21:44:36.732570+08:00
        date_time = (date_time['datetime'])
        
        # extract just the date 
        date = date_time[0:10]
        # strip the - from the date
        date = date.replaces('-', '')
        # extract just the time
        current_time =  date_time[11:19]
        # strip the : from the time
        current_time = current_time.replaces(':', '')

        return date + current_time

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


class MainLoop():
    ''' Main function where the clock spends its time, doing clock things '''
    def __init__(self,device_type, socket_count, serial_device):
        self.device_type = device_type
        self.serial_device = serial_device


    def main(self):
        while True:
            get_time = get_time_data_data(self.device_type)
            current_time = format_time(get_time)
            if current_time[4::] == '10':
                self.read_temp_sensor()
            elif current_time[2::] == '1500':
                self.cathode_poisoning_prevention(6)
            elif current_time[2::] == '4100':
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
        print('date to print : ')
        print(date)
        time.sleep(1)
        b7_message(self.serial_device, date)
        time.sleep(1)


    def cathode_poisoning_prevention(self):
        # set effect speed to 1 second
        b7_effect_speed('/dev/ttyUSB0', '1' * self.socket_count)
        try:
            # Effect type 8, spin full cycle
            b7_effect('/dev/ttyUSB0', '8' * self.socket_count)
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

    MainLoop.main('pc', '6', '/dev/ttyUSB0')

