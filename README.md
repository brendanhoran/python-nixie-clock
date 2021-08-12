# Python Nixie Clock (+ ESP32/MicroPython)
Python code to drive Nixie smart sockets   
## VERY MUCH DEV IN PROGRESS!!!!!   

### What works
* ONLY can drive smart sockets at the moment.   
* Gets time and date biased off Geo located IP.    
* Supports ESP32 and local Linux serial port modes (can be driven from a serial port under linux or burnt into MicroPython F/W)   

### Whats not working (but will oneday)
* Direct drive of any non smart socket nixie tube   
* Way to much is hard coded   
* H/V shutdown
* Smart socket tube setting / per tube / at all   
* Reading temp/humidity sensors   
#### Whats hard coded...   
* machine UART pin number   
* Serial device for PC/linux mode   
* Time format 12/24h   
* Date format (range of types supported)   
* What to do on 10/15/3060min window intervals
* What time the intervals are   


### How to build    
**NOTE** this is ONLY needed for ESP32 mode.   
Uses [Earthly.dev](https://earthly.dev) to build the latests MicroPython F/W based on a set tag of the Espressif framework.   
#### Build firmware   
earthly +firmware   
#### Program ESP32   
earthly --build-arg SERIAL_PORT=/dev/ttyUSB0 +flash   

** WHere `/dev/ttyUSB` is your ESP32 device.   

#### Example main.py
```
import wifi_setup
import clock
wifi_setup = wifi_setup.WIFI_setup('AP_SSID','YOUR_PASSWORD')
wifi_setup.connect()

# Run in 24 Hour mode, with 6 sockets and date format of DD-MM-YY on an ESP32 device.   
# Breakdown of the function: clock.MainLoop(DEVICE TYPE, SOCKET COUNT, TIME FORMAT, DATE FORMAT, SERIAL DEVICE)
run = clock.MainLoop('micropython','6','24h', 'DDMMYY', 'micropython')
run.main()
```

### Local Linux mode   
Set up your serial device and time preferences in the code and run `modules/clock.py`.   


### External dependence's
* [Smart sockets](https://groups.io/g/smartsockets) 
* If using Micropython ( All from https://github.com/micropython/micropython-lib )
  * urequests
  * datetime

