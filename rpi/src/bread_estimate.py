import numpy as np
from collections import deque
import requests
import random
import time

url =''

def generate_data(i):
    temp = random.choice(range(18,30))
    humid = random.choice(range(60,100))
    co2 = random.choice(range(400,2000))
    dist = list(reversed(range(0,150)))
    return [temp,humid,co2,dist[i]]
    #average 10 data points on each sensor

def get_data(url):
    data= requests.get(url).json()
    return data
    
proving = True
temp =[]
humid=[]
co2=[]
height=[]
bowl_height = 250
target_growth = 2 #many recipes say doubled in size 
i=0
rate = []
while proving:
    data = generate_data(i)
    print(data)
    temp.append(data[0])
    humid.append(data[1])
    co2.append(data[2])
    height.append(250-data[3])
    if len(height)>1:
        rate=np.gradient(height)
    if len(rate)>1:
        dev2 = np.gradient(rate)
    i+=1
    if i==150:
        proving = False
    time.sleep(10)
print(temp,humid,co2,height)
print (rate)
print (dev2)
