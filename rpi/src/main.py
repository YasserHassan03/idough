import time
import smbus2
import requests as r
import board
import busio
import adafruit_vl53l0x

i2c = busio.I2C(board.SCL, board.SDA)
tofSensor = adafruit_vl53l0x.VL53L0X(i2c)

import urllib3

urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

class MySensor:
    def __init__(self, address=0x40): # default temperature master hold
        self.add = address
        self.tempCommand = 0xe3 # Temperature, Master No Hold
        self.humidityCommand = 0xe5 # Relative Humidity, Master No Hold
        self.bus = smbus2.SMBus(1)
    
    def read(self):
        self._updateSensor(self.tempCommand)
        temperatureReading = self._getReading(2)
        self._updateSensor(self.humidityCommand)
        humidityReading = self._getReading(1)
        return self._convertToCelcius(temperatureReading), self._convertToRH(humidityReading)

    def _getReading(self, sensor):
        result = smbus2.i2c_msg.read(self.add, sensor)
        self.bus.i2c_rdwr(result)
        return int.from_bytes(result.buf[0] + result.buf[1], 'big')
        
    def _convertToRH(self, reading):
        return ((125 * reading) / 65536) - 6

    def _convertToCelcius(self, reading):
        return ((175.72 * reading) / 65536) - 46.85

    def _updateSensor(self, command):
        cmd_meas = smbus2.i2c_msg.write(self.add, [command])
        self.bus.i2c_rdwr(cmd_meas)
           
def main():
    url = "https://ec2-52-90-198-47.compute-1.amazonaws.com:5000/"
    samplingTime = 1
    sensor = MySensor()
    tofReading = tofSensor.range

    while True:
        temp, rh = sensor.read()

        data = {"temp":temp, "humid":rh, "tof":tofReading, "samplingTime":samplingTime}
        print(f'temp:{temp}, humidity:{rh}')
        backPressure = r.post(url=url+"/", json=data, verify='./certificate.crt')

        data = backPressure.json()
        samplingTime = data['sampling']
        print(f'response: {data}')


        time.sleep(samplingTime)

if __name__ == "__main__":
    main()



