import numpy as np
import random
from scipy.signal import convolve
import matplotlib.pyplot as plt
from collections import deque


def generateRandomData():
    return random.randint(-10, 10)

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)

def fromMatlab():
    st = "0.0151    0.0366    0.0921    0.1567    0.1995    0.1995    0.1567    0.0921    0.0366    0.0151"
    return np.array([float(i) for i in st.split(" ") if i != "" and i != " "])

def main():
    N = 10
    # filter = np.zeros((1,10))
    
    q = deque([0]*N)
    means = []
    readings = []
    b = fromMatlab()

    for _ in range(1, 100):
        if len(q) >= N:
            q.popleft()
        
        reading = generateRandomData();
        readings.append(reading)
        q.append(reading)

        assert len(q) == len(b)

        y = convolve(q, b, mode='valid')
        print(f'y: {y}') 
        means.append(y[0])

    print(f'Means: {means}')
    plt.plot(means)
    plt.plot(readings)
    plt.show()


if __name__ == "__main__":
    main()
