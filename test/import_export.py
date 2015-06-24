import csv
import math
import numpy as np

def export(data, name):
    with open(name+'.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(data)

data = [[math.sin(2*math.pi*t)+.1*t,math.cos(2*math.pi*t)] for t in np.arange(0,10,.01)]
export(data, 'cheesy')
