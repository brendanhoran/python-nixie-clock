# Serial port access: Serial is for Linux, machine is for MicroPython
try:
    import serial
except ImportError:
    from machine import UART, RTC

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
        uart.init(9600, bits=8, parity=None, stop=1, tx=26)
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
