import config
import machine
import temperature_sensor
import utils

utils.printInfo("NODEMCU", "thermometer low power boot up")

_temperature_sensor = temperature_sensor.TemperatureSensor(machine.Pin(config.DS18B20_PIN))
_temperature_sensor.update()
_temperature_sensor.upload()

rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
rtc.alarm(rtc.ALARM0, 60000)

machine.deepsleep()
