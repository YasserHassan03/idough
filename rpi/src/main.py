import time
import smbus2
import requests as r

class Temp_Humid_Sensor:
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

class Gas_Sensor:
    def __init__(self, address=0x5A):
        self.add = address
        self.status = 0x00
        self.mode = 0x01
        self.result = 0x02
        self.bus = smbus2.SMBus(1)

    def read_ccs811_data(self):
    # Check if data is ready
        ready = self.bus.read_byte_data(self.add, self.status)
        if ready & (1 << 3):  # Bit 3 indicates data ready
            # Read the data
            data = self.bus.read_i2c_block_data(self.add, self.result, 8)  
            # Process the data
            co2 = (data[0] << 8) | data[1]
            tvoc = (data[2] << 8) | data[3]
            return co2, tvoc
        else:
            return None


            
def main():
    url = ""
    samplingTime = 0.1
    T_H_sensor = Temp_Humid_Sensor()
    Gas_Sensor = Gas_Sensor()
    while True:
        temp, rh = T_H_sensor.read()
        print(f'temp:{temp}, humidity:{rh}')
        co2, tvoc = Gas_Sensor.read_ccs811_data()
        print(f'co2:{co2}, tvoc:{tvoc}')
        # backPressure = r.post(url=url, data={"temp":temp, "humid":rh}) 
        
        #TODO: If needed, implement back pressure, i.e make sample time inversly proportional to value obtained from server   
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()



