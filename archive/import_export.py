import csv
import math
import numpy as np

def export(data, name):
    path = name + '.csv'
    with open(path, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(data)
