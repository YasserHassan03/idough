import time
import smbus2
import requests as r
import board
import busio
import adafruit_vl53l0x
from abc import abstractmethod
import numpy as np
from collections import deque
from scipy.signal import convolve
import urllib3
import threading
from enum import Enum

# urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
urllib3.disable_warnings()

# Abstract class 
class MySensor: 
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplemented
    
    @abstractmethod 
    def read(self): # Return all data from sensor
        raise NotImplemented

    @abstractmethod 
    def readFiltered(self):
        raise NotImplemented

 
class LowPassFilter: # Wrapper class, which implements a low pass filter for a given sensor 
    def __init__(self, N = 10) -> None:
        self.b = np.array([0.0151, 0.0366, 0.0921, 0.1567, 0.1995, 0.1995, 0.1567, 0.0921, 0.0366, 0.0151])  
        self.N = N 

    def filter(self, q: deque):       
        assert len(q) == len(self.b)

        y = convolve(q, self.b, mode='valid')
        
        return y[0]

    def sample(self, q: deque, reading: float):
        if len(q) >= self.N:
            q.popleft()
        
        q.append(reading)

        return q

  
class Si7021Sensor(MySensor, LowPassFilter):
    def __init__(self, address=0x40, N=10): # default temperature master hold
        self.add = address
        self.tempCommand = 0xe3 # Temperature, Master No Hold
        self.humidityCommand = 0xe5 # Relative Humidity, Master No Hold
        self.bus = smbus2.SMBus(1)
        self.qTemp = deque([0]*N)
        self.qHumid = deque([0]*N)
        super().__init__() 


    def read(self):
        return self.read_temp(), self.read_humid() 
  
    
    def readFiltered(self):
        return self.filteredTemp(), self.filteredHumid()
    
    def read_temp(self):          
        return self._read(self.tempCommand, 2, self._convertToCelcius)
    
    def read_humid(self): 
        return self._read(self.humidityCommand, 1, self._convertToRH)

    def filteredTemp(self):
        return self.filter(self.qTemp)

    def filteredHumid(self): 
        return self.filter(self.qHumid)

    def sampleSi7021(self):
        self.qTemp = self.sample(self.qTemp, self.read_temp())
        self.qHumid = self.sample(self.qHumid, self.read_humid())
        return 1

    def _read(self, command, register, conversion):
        self._updateSensor(command)
        temperatureReading = self._getReading(register)
        return conversion(temperatureReading)

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
    


class TofSensor(MySensor, LowPassFilter):
    def __init__(self, N=10) -> None:
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor =  adafruit_vl53l0x.VL53L0X(self.i2c)
        self.qDistance = deque([0]*N)
        super().__init__()   

    def read(self):
        return float(self.sensor.range) 


    def readFiltered(self):
        return self.filteredTof()

    def filteredTof(self):
        return self.filter(self.qDistance)
    
    def sampleTof(self):
        
        self.qDistance = self.sample(self.qDistance, self.read())
        return 1

class State(Enum):
    Registration=1
    Active=2
    
def main():

    url = "https://ec2-52-90-182-98.compute-1.amazonaws.com:"
    pId = 123
    state = State.Registration
    port = None 

    samplingTime = 1
    
    tempAndHumidSensor = Si7021Sensor()
    tofSensor = TofSensor()
        
    def sampleData():
        filterSamplingTime = 0.2
        while True:
            tempAndHumidSensor.sampleSi7021()
            tofSensor.sampleTof()
            time.sleep(filterSamplingTime)


    filteringThread = threading.Thread(sampleData())
     
    while True:
        if state == State.Registration:
            res = r.post(url=url+"5000/register", json={"pId":pId}, verify=False)
            
            if res.status_code == 200: 
                state = State.Active
                port = res.json()['port']
                filteringThread.start() 

            time.sleep(samplingTime)
            continue
        
        temp, rh = tempAndHumidSensor.readFiltered()
        distance = tofSensor.readFiltered()

        data = {"temp":temp, "humid":rh, "tof":distance, "sampling":samplingTime}
        print(f'temp:{temp}, humidity:{rh}, tof:{distance}')

        # backPressure = r.post(url=url+"/", json=data, verify='./certificate.crt')
        backPressureResponse = r.post(url=url+f"{port}/sensors", json=data, verify=False)
        
        if backPressureResponse.status_code != 200:
            port = None
            state = State.Registration
            filteringThread.join()

            continue

        data = backPressureResponse.json()
        samplingTime = data['sampling']
        print(f'response: {data}')

        time.sleep(samplingTime)


if __name__ == "__main__":
    main()



