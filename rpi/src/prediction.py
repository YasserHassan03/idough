import numpy as np
from collections import deque
import requests
import random
import time

class breadPredictor:
    def __init__(self, recipeTime=120, bowlHeight=250, targetGrowth=2, yeast=3, salt=6, flour=500, water=350):

        self.height=[]
        self.temp = []
        self.humid = []
        self.growthRate=[]
        self.growthRatedx2=[]
        self.recipeTime = recipeTime
        self.timeForecast= None #proving time default 120 mins
        self.bowlHeight=bowlHeight #assuming 250mm bowl
        self.targetGrowth=targetGrowth #many recipes say doubled in size
        self.yeastRatio=100*yeast/flour
        self.saltRatio=100*salt/flour
        self.waterRatio=100*water/flour

    def calulateHeight(self):
        return self.bowlHeight - self.distance

    #def predictTime(self):
    
    def tempWeight(self):
        curTemp = self.temp[-1]
        if curTemp>15 and curTemp<=33:
            return (-3/18)*curTemp + 7.5
        elif curTemp > 33 and curTemp < 40:
            return (3/7)*curTemp - 12
        else :
            return self.recipeTime*4   #temperature out of range
    
    def humidWeight(self):
        curHumid = self.humid[-1]
        if curHumid<=80:
            return self.recipeTime/(curHumid*1/80)
        elif curHumid>80:
            return self.recipeTime/((-curHumid*0.1/20)+1.4)
        else:
            return self.recipeTime  #humidity out of range
        
    def insertData(self, distance, temp, humid):
        self.height.append(self.calculateHeight(distance, self.bowlHeight))
        self.temp.append(temp)
        self.humid.append(humid)
        return True
    
    def gradCalc(self):
        if len(self.height)>1:
            self.growthRate=np.gradient(self.height)
        if len(self.growthRate)>1:
            self.growthRatedx2 = np.gradient(self.growthRate)
        return self.growthRate, self.growthRatedx2

