import time
import smbus2
import pthreading
import threading

class MySensor:
    
    def __init__(self, address=0x40, samplingTime=1, useSamplingThread=1): # default temperature master hold
        self.add = address
        self.tempCommand = 0xf3 # Temperature, Master No Hold
        self.humidityCommand = 0xf5 # Relative Humidity, Master No Hold
        self.bus = smbus2.SMBus(1)
        self.samplingTime = samplingTime
        self.useSamplingThread = useSamplingThread
        self.samplingThread = threading.Thread(target=self._sample) if useSamplingThread else None

        if useSamplingThread: 
            self.samplingThread.start()
                
    def __del__(self):
        if self.useSamplingThread: 
            self.samplingThread.join()
     
    def read(self):
        if not self.useSamplingThread:
            self._updateSensor();
                
        temperatureReading = self._getReading(2)
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

    def _updateSensor(self):
        cmd_meas_tmp = smbus2.i2c_msg.write(self.add, [self.tempCommand])
        cmd_meas_hmd = smbus2.i2c_msg.write(self.add, [self.humidityCommand])

        self.bus.i2c_rdwr(cmd_meas_tmp)
        time.sleep(0.1)
        self.bus.i2c_rdwr(cmd_meas_hmd)

    def _sample(self):
        while True:
            time.sleep(self.samplingTime)
            self._updateSensor()
            
            
def main():
    sensor = MySensor()
    while True:
        temp, rh = sensor.read()
        print(f'temp:{temp}, humidity:{rh}')

        time.sleep(2)


if __name__ == "__main__":
    main()



