from machine import Pin, PWM
import onewire
import ds18x20
import utime as time
import socket

PWM_CLOCK = 1000
DALLAS_PIN = 0 #D3
PUMP_PIN = 13 #D7
HEATER_PIN = 14 #D5
FAN_PIN = 12 #D6
INTERNAL_DALLAS_ID = '28eea34625160109'
UPLOADER_KEY = 'YOUR_API_KEY'

class Devices:
    def __init__(self):
        self.pumpPwm = PWM(Pin(PUMP_PIN), freq=PWM_CLOCK, duty=0)
        self.heaterPwm = PWM(Pin(HEATER_PIN), freq=PWM_CLOCK, duty=0)
        self.fanPwm = PWM(Pin(FAN_PIN), freq=PWM_CLOCK, duty=0)
        self.sound = False
        self.dallas = ds18x20.DS18X20(onewire.OneWire(Pin(DALLAS_PIN)))
        self.externalTemperatures = {}
        self.internalTemperature = 0.0

    @staticmethod
    def calculateDutyToPercent(value):
        return int(round(value / 1023.0 * 100.0))

    @staticmethod
    def calculatePercentToDuty(value):
        return int(round(value / 100.0 * 1023.0))

    def getPump(self):
        return Devices.calculateDutyToPercent(self.pumpPwm.duty())

    def setPump(self, value):
        self.pumpPwm.duty(Devices.calculatePercentToDuty(value))

    def getHeater(self):
        return Devices.calculateDutyToPercent(self.heaterPwm.duty())

    def setHeater(self, value):
        self.heaterPwm.duty(Devices.calculatePercentToDuty(value))

    def getFan(self):
        return Devices.calculateDutyToPercent(self.fanPwm.duty())

    def setFan(self, value):
        self.fanPwm.duty(Devices.calculatePercentToDuty(value))

    def getSound(self):
        return self.sound

    def setSound(self, value):
        self.sound = value

    def getInternalTemperature(self):
        return self.internalTemperature

    def getExternalTemperatures(self):
        return list(self.externalTemperatures.values())

    def getAverageExternalTemperature(self):
        if not self.externalTemperatures:
            return 0.0
        return sum(self.externalTemperatures.values())/len(self.externalTemperatures)

    def update(self):
        self.internalTemperature = 0.0
        self.externalTemperatures = {}
        roms = self.dallas.scan()
        self.dallas.convert_temp()
        for rom in roms:
            id = "".join("{:02x}".format(c) for c in rom)
            temperature = self.dallas.read_temp(rom)
            if temperature != 85.0:
                if id == INTERNAL_DALLAS_ID:
                    self.internalTemperature = temperature
                else:
                    self.externalTemperatures[id] = temperature
                # print('%s %.2f' % (id, temperature))
        # print('')

    def upload(self):
        for (serial, temperature) in self.externalTemperatures.items():
            self.uploadTemperature(serial, temperature)
        self.uploadTemperature(INTERNAL_DALLAS_ID, self.internalTemperature)

    def uploadTemperature(self, serial, temperature):
        url = "http://monitor.shajen.pl/api/temp/add?serial=%s&temperature=%.2f&key=%s" % (serial, temperature, UPLOADER_KEY)
        Devices.httpGet(url)

    @staticmethod
    def httpGet(url):
        _, _, host, path = url.split('/', 3)
        addr = socket.getaddrinfo(host, 80)[0][-1]
        s = socket.socket()
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
        s.close()
