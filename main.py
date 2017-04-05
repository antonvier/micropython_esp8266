from machine import Pin, I2C, Timer
import devices
import brew
import display
import server

i2c = I2C(scl=Pin(4), sda=Pin(5), freq=400000) #D2 D1

_devices = devices.Devices()
_brew = brew.Brew(_devices)
_display = display.Display(i2c, _devices)
_server = server.Server(33455, _devices, _brew, _display)

def update(timer):
    _display.update()
    _devices.update()

tim1 = Timer(0)
tim1.init(period=1000, mode=Timer.PERIODIC, callback=update)
tim2 = Timer(1)
tim2.init(period=60000, mode=Timer.PERIODIC, callback=lambda t: _devices.upload())

_server.run()
