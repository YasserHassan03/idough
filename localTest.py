import numpy as np
from collections import deque
import time
import smbus2
import requests as r
import board
import busio
import adafruit_vl53l0x
#
class breadPredictor:
    def __init__(self, recipeTime=120, bowlHeight=250, targetGrowth=2, yeast=3, salt=6, flour=500, water=350):
        self.height = deque(maxlen=10)
        self.temp = deque(maxlen=10)
        self.humid = deque(maxlen=10)
        self.growthRate = deque(maxlen=10)
        self.recipeTime = recipeTime  # proving time according to recipe default 120 mins
        self.timeForecast = None
        self.bowlHeight = bowlHeight  # assuming 250mm bowl
        self.targetGrowth = targetGrowth  # many recipes say doubled in size
        self.yeastRatio = 100 * yeast / flour
        self.saltRatio = 100 * salt / flour
        self.waterRatio = 100 * water / flour
        self.tempWarning = False
        self.humidWarning = False
        self.heightWarning = False
        self.done = False
        self.sampleTime = 1

    def getWarning(self):
        return self.tempWarning, self.humidWarning, self.heightWarning

    def calulateHeight(self, distance):
        return self.bowlHeight - distance + 30 #sensor calibration

    def recipeWeight(self):
        yeastGrad = self.recipeTime / (self.yeastRatio / 0.6)
        saltGrad = self.recipeTime / (self.saltRatio / 1.2)
        return 0.7 * yeastGrad + 0.3 * saltGrad

    def predictTime(self):
        if self.done:  # bread is done
            self.timeForecast = 0
        else:
            self.timeForecast = 0.4 * self.tempWeight() + 0.1 * self.humidWeight() + 0.5 * self.heightWeight()
        return self.timeForecast

    def tempWeight(self):
        curTemp = self.temp[-1]
        if curTemp > 15 and curTemp <= 35:
            return self.recipeTime / (curTemp * 1 / 15 - 2 / 3)
        elif curTemp > 35 and curTemp < 40:
            return self.recipeTime / (-curTemp * 0.2 + 1.46)
        else:
            self.tempWarning = True  # temperature out of range for bread making
            return self.recipeTime * 4  # assume time is 4 times longer for temperature out of range

    def humidWeight(self):
        curHumid = self.humid[-1]
        if curHumid <= 80 and curHumid > 20:
            return self.recipeTime / (curHumid * 1 / 80)
        elif curHumid > 80:
            return self.recipeTime / ((-curHumid * 0.1 / 20) + 1.4)
        else:
            self.humidWarning = True  # humidity out of range for bread making
            return self.recipeTime  # humidity out of ideal range for bread making doesn't make huge difference

    def heightWeight(self): #fix this u rat
        curSampleTime = self.sampleTime  
        if self.height[0] * self.targetGrowth > self.bowlHeight:
            self.heightWarning = True  # bread is too big for bowl
        if len(self.height) < 2:
            return self.recipeTime  # not enough data to change predict
        elif self.height[-1] == self.height[0] * self.targetGrowth or self.height[-1] > self.bowlHeight:
            self.done = True  # bread is done
            return 0
        else:
            self.gradCalc()
            curGrowthRate = self.growthRate[-1]  # growth rate in mm/sampleTime
            if curGrowthRate > 0:
                if self.height[-1] < self.bowlHeight:
                    self.sampleTime -= 10  # decrease sample time (rate of growth is increasing)
                    targetHeight = max(self.height[0] * self.targetGrowth, self.bowlHeight)
                    timeLeft = (targetHeight - self.height[-1]) / curGrowthRate  # latest growth rate based time pred in sampleTimes
                    return timeLeft*curSampleTime / 60  # in minutes
            else:
                self.sampleTime+=10 #increase sample time
                return self.recipeTime  # dough not growing right now

    def insertData(self, distance, temp, humid):
        self.height.append(self.calulateHeight(distance))
        self.temp.append(temp)
        self.humid.append(humid)
        return True

    def gradCalc(self):
        if len(self.height) > 1:
            self.growthRate = np.gradient(self.height)
        return self.growthRate


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
    predictor = breadPredictor()
    samplingTime = 1
    i2c = busio.I2C(board.SCL, board.SDA)
    tofSensor = adafruit_vl53l0x.VL53L0X(i2c)   
    sensor = MySensor()
    while True:
        tofReading = tofSensor.range    
        temp, rh = sensor.read()
        print(f'temp:{temp}, humidity:{rh}, tof:{tofReading}')
        predictor.insertData(distance=tofReading, temp=temp, humid=rh) 
        timeRemaining = predictor.predictTime()
        print(f'Time Remaining: {timeRemaining}')
        print(f'Height {predictor.height}')
        print(f'Derivative {predictor.growthRate}')
        print(f'Weights: temp {predictor.tempWeight()}, humid {predictor.humidWeight()},height {predictor.heightWeight()}')

        time.sleep(samplingTime)

if __name__ == "__main__":
    main()

