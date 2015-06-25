import csv
import math
import numpy as np

def export(data, name):
    with open(name+'.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(data)

