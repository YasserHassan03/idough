import numpy as np
from collections import deque
# import requests
# import random



class BreadPredictor:
    def __init__(self, recipeTime=120, bowlHeight=100, targetGrowth=2, yeast=3, salt=6, flour=500, water=350, sampleTime=1):
        self.height = deque(maxlen=10)
        self.originalHeight = 0
        self.temp = deque(maxlen=10)
        self.humid = deque(maxlen=10)
        self.growthRate = deque(maxlen=10)
        self.recipeTime = recipeTime  # proving time according to recipe default 120 mins
        self.ingredientTime = recipeTime #initial time prediction based on ingredients
        self.tempHumidTime = recipeTime #dynamic time prediction based on temp and humidity
        self.tempHeightTime = recipeTime #dynamic time prediction based on height
        self.timeForecast = None #overall time prediction
        self.bowlHeight = bowlHeight  # assuming 250mm bowl
        self.targetGrowth = targetGrowth  # many recipes say doubled in size+
        self.yeastRatio = 100 * yeast / flour
        self.saltRatio = 100 * salt / flour
        self.waterRatio = 100 * water / flour
        self.tempWarning = False
        self.humidWarning = False
        self.heightWarning = False
        self.done = False
        self.sampleTime = sampleTime/60  # in minutes

    def getWarning(self):
        return self.tempWarning, self.humidWarning, self.heightWarning

    def calulateHeight(self, distance):
        return self.bowlHeight - distance #sensor calibration

    def ingredWeight(self):
        yeastGrad = self.ingredientTime / (self.yeastRatio / 0.6)
        saltGrad = self.ingredientTime / (self.saltRatio / 1.2)
        self.ingredientTime = 0.7 * yeastGrad + 0.3 * saltGrad
        return 0.7 * yeastGrad + 0.3 * saltGrad

    def predictTime(self):
        if self.done: 
            self.timeForecast = 0
        else: 
            self.timeForecast = 0.01*self.heightWeight()  + 0.69 * self.ingredientTime + 0.2*self.tempWeight() + 0.1*self.humidWeight()
        return self.timeForecast

    def tempWeight(self):
        curTemp = self.temp[-1]
        if curTemp > 15 and curTemp <= 35:
            return self.ingredientTime / (curTemp * 1 / 15 - 2 / 3)
        elif curTemp > 35 and curTemp < 40:
            return self.ingredientTime / (-curTemp * 0.2 + 1.46)
        else:
            self.tempWarning = True  # temperature out of range for bread making
            return self.recipeTime * 4  # assume time is 4 times longer for temperature out of range

    def humidWeight(self):
        curHumid = self.humid[-1]
        if curHumid <= 80 and curHumid > 20:
            return self.ingredientTime / (curHumid * 1 / 80)
        elif curHumid > 80:
            return self.ingredientTime / ((-curHumid * 0.1 / 20) + 1.4)
        else:
            self.humidWarning = True  # humidity out of range for bread making
            return self.recipeTime  # humidity out of ideal range for bread making doesn't make huge difference

    def heightWeight(self): #fix this u rat
        curSampleTime = self.sampleTime
        if self.height[0] * self.targetGrowth > self.bowlHeight:
            self.heightWarning = True  # bread is too big for bowl
        if len(self.height) < 2:
            return self.ingredientTime  # not enough data to change predict
        elif self.height[-1] == self.height[0] * self.targetGrowth or self.height[-1] > self.bowlHeight:
            self.done = True  # bread is done
            return 0
        else:
            self.gradCalc()
            curGrowthRate = self.growthRate[-1]  # growth rate in mm/sampleTime
            if curGrowthRate > 0:
                if self.height[-1] < self.bowlHeight:
                    #self.sampleTime -= 10  # decrease sample time (rate of growth is increasing)
                    targetHeight = max(self.originalHeight* self.targetGrowth, self.bowlHeight)
                    timeLeft = (targetHeight - self.height[-1]) / curGrowthRate  # latest growth rate based time pred in sampleTimes
                    print("timeleft", timeLeft)
                    return timeLeft*curSampleTime  # in minutes
            else:
                #self.sampleTime+=10 #increase sample time
                return self.recipeTime  # dough not growing right now

    def insertData(self, distance, temp, humid):
        if len(self.height) == 0:
            self.originalHeight = self.calulateHeight(distance)
        self.height.append(self.calulateHeight(distance))
        self.temp.append(temp)
        self.humid.append(humid)
        self.ingredientTime -= self.sampleTime
        return True

    def gradCalc(self):
        if len(self.height) > 1:
            self.growthRate = np.gradient(self.height)
        return self.growthRate



# class BreadPredictor:
#     def __init__(self, recipeTime=120, bowlHeight=250, targetGrowth=2, yeast=3, salt=6, flour=500, water=350):
#         self.height = deque(maxlen=10)
#         self.temp = deque(maxlen=10)
#         self.humid = deque(maxlen=10)
#         self.growthRate = deque(maxlen=10)
#         self.recipeTime = recipeTime  # proving time according to recipe default 120 mins
#         self.timeForecast = None
#         self.bowlHeight = bowlHeight  # assuming 250mm bowl
#         self.targetGrowth = targetGrowth  # many recipes say doubled in size
#         self.yeastRatio = 100 * yeast / flour
#         self.saltRatio = 100 * salt / flour
#         self.waterRatio = 100 * water / flour
#         self.tempWarning = False
#         self.humidWarning = False
#         self.heightWarning = False
#         self.done = False
#         self.sampleTime = 1
#
#     def getWarning(self):
#         return self.tempWarning, self.humidWarning, self.heightWarning
#
#     def calulateHeight(self, distance):
#         return self.bowlHeight - distance + 30 #sensor calibration
#
#     def recipeWeight(self):
#         yeastGrad = self.recipeTime / (self.yeastRatio / 0.6)
#         saltGrad = self.recipeTime / (self.saltRatio / 1.2)
#         return 0.7 * yeastGrad + 0.3 * saltGrad
#
#     def predictTime(self):
#         if self.done:  # bread is done
#             self.timeForecast = 0
#         else:
#             self.timeForecast = 0.4 * self.tempWeight() + 0.1 * self.humidWeight() + 0.5 * self.heightWeight()
#         return self.timeForecast
#
#     def tempWeight(self):
#         curTemp = self.temp[-1]
#         if curTemp > 15 and curTemp <= 35:
#             return self.recipeTime / (curTemp * 1 / 15 - 2 / 3)
#         elif curTemp > 35 and curTemp < 40:
#             return self.recipeTime / (-curTemp * 0.2 + 1.46)
#         else:
#             self.tempWarning = True  # temperature out of range for bread making
#             return self.recipeTime * 4  # assume time is 4 times longer for temperature out of range
#
#     def humidWeight(self):
#         curHumid = self.humid[-1]
#         if curHumid <= 80 and curHumid > 20:
#             return self.recipeTime / (curHumid * 1 / 80)
#         elif curHumid > 80:
#             return self.recipeTime / ((-curHumid * 0.1 / 20) + 1.4)
#         else:
#             self.humidWarning = True  # humidity out of range for bread making
#             return self.recipeTime  # humidity out of ideal range for bread making doesn't make huge difference
#
#     def heightWeight(self): #fix this u rat
#         curSampleTime = self.sampleTime
#         if self.height[0] * self.targetGrowth > self.bowlHeight:
#             self.heightWarning = True  # bread is too big for bowl
#         if len(self.height) < 2:
#             return self.recipeTime  # not enough data to change predict
#         elif self.height[-1] == self.height[0] * self.targetGrowth or self.height[-1] > self.bowlHeight:
#             self.done = True  # bread is done
#             return 0
#         else:
#             self.gradCalc()
#             curGrowthRate = self.growthRate[-1]  # growth rate in mm/sampleTime
#             if curGrowthRate > 0:
#                 if self.height[-1] < self.bowlHeight:
#                     self.sampleTime -= 10  # decrease sample time (rate of growth is increasing)
#                     targetHeight = max(self.height[0] * self.targetGrowth, self.bowlHeight)
#                     timeLeft = (targetHeight - self.height[-1]) / curGrowthRate  # latest growth rate based time pred in sampleTimes
#                     return timeLeft*curSampleTime / 60  # in minutes
#             else:
#                 self.sampleTime+=10 #increase sample time
#                 return self.recipeTime  # dough not growing right now
#
#     def insertData(self, distance, temp, humid):
#         self.height.append(self.calulateHeight(distance))
#         self.temp.append(temp)
#         self.humid.append(humid)
#         return True
#
#     def gradCalc(self):
#         if len(self.height) > 1:
#             self.growthRate = np.gradient(self.height)
#         return self.growthRate
#






# class breadpredictor:
#     def __init__(self, recipetime=120, bowlheight=250, targetgrowth=2, yeast=3, salt=6, flour=500, water=350, sampletime=1):
#         self.height = deque(maxlen=10)
#         self.originalheight = 0
#         self.temp = deque(maxlen=10)
#         self.humid = deque(maxlen=10)
#         self.growthrate = deque(maxlen=10)
#         self.recipetime = recipetime  # proving time according to recipe default 120 mins
#         self.ingredienttime = recipetime #initial time prediction based on ingredients
#         self.temphumidtime = recipetime #dynamic time prediction based on temp and humidity
#         self.tempheighttime = recipetime #dynamic time prediction based on height
#         self.timeforecast = none #overall time prediction
#         self.bowlheight = bowlheight  # assuming 250mm bowl
#         self.targetgrowth = targetgrowth  # many recipes say doubled in size+
#         self.yeastratio = 100 * yeast / flour
#         self.saltratio = 100 * salt / flour
#         self.waterratio = 100 * water / flour
#         self.tempwarning = false
#         self.humidwarning = false
#         self.heightwarning = false
#         self.done = false
#         self.sampletime = sampletime/60  # in minutes
#
#     def getwarning(self):
#         return self.tempwarning, self.humidwarning, self.heightwarning
#
#     def calulateheight(self, distance):
#         return self.bowlheight - distance #sensor calibration
#
#     def ingredweight(self):
#         yeastgrad = self.ingredienttime / (self.yeastratio / 0.6)
#         saltgrad = self.ingredienttime / (self.saltratio / 1.2)
#         self.ingredienttime = 0.7 * yeastgrad + 0.3 * saltgrad
#         return 0.7 * yeastgrad + 0.3 * saltgrad
#
#     def predicttime(self):
#         if self.done: 
#             self.timeforecast = 0
#         else: 
#             print(f'hw:{self.heightweight()}, recipetime: {self.recipetime}tempw: {self.tempweight()} humidw: {self.humidweight()}')
#             self.timeforecast = 0.3*self.heightweight() + 0.4* self.recipetime + 0.2*self.tempweight() + 0.1*self.humidweight()
#         return self.timeforecast
#
#     def tempweight(self):
#         curtemp = self.temp[-1]
#         if curtemp > 15 and curtemp <= 35:
#             return self.ingredienttime / (curtemp * 1 / 15 - 2 / 3)
#         elif curtemp > 35 and curtemp < 40:
#             return self.ingredienttime / (-curtemp * 0.2 + 1.46)
#         else:
#             self.tempwarning = true  # temperature out of range for bread making
#             return self.recipetime * 4  # assume time is 4 times longer for temperature out of range
#
#     def humidweight(self):
#         curhumid = self.humid[-1]
#         if curhumid <= 80 and curhumid > 20:
#             return self.ingredienttime / (curhumid * 1 / 80)
#         elif curhumid > 80:
#             return self.ingredienttime / ((-curhumid * 0.1 / 20) + 1.4)
#         else:
#             self.humidwarning = true  # humidity out of range for bread making
#             return self.recipetime  # humidity out of ideal range for bread making doesn't make huge difference
#
#     def heightweight(self): #fix this u rat
#         cursampletime = self.sampletime
#
#         if self.height[0] * self.targetgrowth > self.bowlheight:
#             self.heightwarning = true  # bread is too big for bowl
#             return 0 # ask later
#
#         if len(self.height) < 2:
#             return self.ingredienttime  # not enough data to change predict
#
#         elif self.height[-1] == self.height[0] * self.targetgrowth or self.height[-1] > self.bowlheight:
#             self.done = true  # bread is done
#             return 0
#
#         else:
#             self.gradcalc()
#             curgrowthrate = self.growthrate[-1]  # growth rate in mm/sampletime
#             if curgrowthrate > 0:
#                 if self.height[-1] < self.bowlheight:
#                     #self.sampletime -= 10  # decrease sample time (rate of growth is increasing)
#                     targetheight = max(self.originalheight* self.targetgrowth, self.bowlheight)
#                     timeleft = (targetheight - self.height[-1]) / curgrowthrate  # latest growth rate based time pred in sampletimes
#                     print("timeleft", timeleft)
#                     return timeleft*cursampletime  # in minutes
#             else:
#                 #self.sampletime+=10 #increase sample time
#                 return self.recipetime  # dough not growing right now
#
#
#     def insertdata(self, distance, temp, humid):
#         if len(self.height) == 0:
#             self.originalheight = self.calulateheight(distance)
#         self.height.append(self.calulateheight(distance))
#         self.temp.append(temp)
#         self.humid.append(humid)
#         self.ingredienttime -= self.sampletime
#         return true
#
#     def gradcalc(self):
#         if len(self.height) > 1:
#             self.growthrate = np.gradient(self.height)
#         return self.growthrate
