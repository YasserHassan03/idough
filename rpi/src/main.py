import time
import smbus2
import requests as r
import board
import busio
import adafruit_vl53l0x
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l0x.VL53L0X(i2c)


class Temp_Humid_Sensor:
    def __init__(self, address=0x40): # default temperature master hold
        self.add = address
        self.tempCommand = 0xe3 # Temperature, Master No Hold
        self.humidityCommand = 0xe5 # Relative Humidity, Master No Hold
        self.bus = smbus2.SMBus(1)
    
    def read_temp(self):
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

class Gas_Sensor(Temp_Humid_Sensor):
    def __init__(self, address=0x5A):
        self.add = address #I2C abed zunji address
        self.status = 0x00
        self.mode = 0x01 #default drive mode read every second
        self.result = 0x02
        self.env = 0x05
        self.bus = smbus2.SMBus(1)
        self.eCO2 = None #pp2
        self.data_ready = None
        self.error = None
        #don't care about volatile compunds
        #self.bus.write_byte_data(self.add, 0xf4)#start firmware
        cmd = smbus2.i2c_msg.write(self.add, [0xf4])
        self.bus.i2c_rdwr(cmd)
        time.sleep(0.1)      
        if self.bus.read_byte_data(self.add, self.status) & 0x80:
            print('Gas sensor started successfully')

    def check_data(self):
        self.data_ready = self.bus.read_byte_data(self.add, self.status) & 0x08
        #print(self.data_ready)
    def check_error(self):
        self.error = self.bus.read_byte_data(self.add, self.status) & 0x01
 
    def read_CO2(self):
        self.check_error()
        self.check_data()
        if self.data_ready:
            CO2_data = (self.bus.read_word_data(self.add, self.result)).to_bytes(2, 'big')
            self._eco2 = (CO2_data[0] << 8) | (CO2_data[1])
        return self.eCO2
            