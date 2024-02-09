import time
import smbus2
import requests as r
import board
import busio
import adafruit_vl53l0x
from abc import abstractmethod
from typing import Callable
import numpy as np
from collections import deque
from scipy.signal import convolve
import urllib3
import threading

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

class LowPassFilter: # Wrapper class, which implements a low pass filter for a given sensor 
    def __init__(self, sensor: MySensor, N = 10) -> None:
        self.sensor = sensor # Will be passed as MySensor.func
        self.b = np.array([0.0151, 0.0366, 0.0921, 0.1567, 0.1995, 0.1995, 0.1567, 0.0921, 0.0366, 0.0151])  
        self.N = N 
   
    # TODO: Implement the filter found in filter.py here
    # See if you need a class, task of fun for this in order to reduce redundancy
    # More importantly, to ensure that the sensor objects are being used correctly
    # It is invalid to have the Si7021Sensor object to be used in two differnet places
    # This means that i might have to seperate their implementaions, having an 
    # Acc 5atrat bi bali fikra, 5ali nafs il beta, bas i3mil LowPassFilter abstract class,
    # o implement seperate filter functions for the tof and si7 classes. Sounds better
    @abstractmethod
    def filter(self):
        raise NotImplemented




class Si7021Sensor(MySensor):
    def __init__(self, address=0x40): # default temperature master hold
        self.add = address
        self.tempCommand = 0xe3 # Temperature, Master No Hold
        self.humidityCommand = 0xe5 # Relative Humidity, Master No Hold
        self.bus = smbus2.SMBus(1)
    
    def read(self):
        return self.read_temp(), self.read_humid() 
   
    def read_temp(self):          
        return self._read(self.tempCommand, 2, self._convertToCelcius)
    
    def read_humid(self): 
        return self._read(self.humidityCommand, 1, self._convertToRH)

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
          

class TofSensor(MySensor):
    def __init__(self) -> None:
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor =  adafruit_vl53l0x.VL53L0X(self.i2c)

    def read(self):
        return float(self.sensor.range) 

def main():
    url = "https://ec2-52-90-182-98.compute-1.amazonaws.com:5000/"
    samplingTime = 1

    
    tempAndHumidSensor = Si7021Sensor()
    tofSensor = TofSensor()


    while True:
        temp, rh = tempAndHumidSensor.read()
        distance = tofSensor.read()

        data = {"temp":temp, "humid":rh, "tof":distance, "sampling":samplingTime}
        print(f'temp:{temp}, humidity:{rh}, tof:{distance}')
        # backPressure = r.post(url=url+"/", json=data, verify='./certificate.crt')
        backPressure = r.post(url=url+"/sensors", json=data, verify=False)

        data = backPressure.json()
        samplingTime = data['sampling']
        print(f'response: {data}')


        time.sleep(samplingTime)

if __name__ == "__main__":
    main()



