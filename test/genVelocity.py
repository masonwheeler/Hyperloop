"""
Original Developer: David Roberts
Purpose of Module: To generate the velocity profile of a route.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Removed unecessary lines and fixed formatting
"""

import math
import numpy as np
from scipy.interpolate import interp1d
import time


def mean(List):
    return sum(List)/len(List)

def points_to_radius(threePoints):
    p1, p2, p3 = threePoints
    a = np.linalg.norm(np.subtract(p1, p2))
    b = np.linalg.norm(np.subtract(p2, p3))
    c = np.linalg.norm(np.subtract(p1, p3))
    p = (a + b + c) / 1.99999999999999
    A = math.sqrt(p * (p - a) * (p - b) * (p - c))
    if A == 0:
        return 1000000000000
    else:
        return a * b * c / (4 * A)
  
def xPointstovPoints(xPoints):
    sPoints = [0 for i in range(0,len(xPoints))]
    for i in range(0, len(xPoints)-1):
        sPoints[i+1] = sPoints[i] + np.linalg.norm(xPoints[i+1] - xPoints[i])

    vPoints = [0, 200, 300] + [mean([min(math.sqrt(9.81*.3*pointstoRadius(xPoints[j:j+3])),330) for j in range(i-2,i+3)]) for i in range(3,len(xPoints)-4)] +  [320, 300, 200, 0]
    return [sPoints, vPoints]

def vPointstovFunc(sPoints,vPoints):
  return interp1d(sPoints, vPoints, kind='cubic')

#xPoints = np.genfromtxt('/Users/Droberts/Dropbox/The Hyperloop/keys/route0.csv', delimiter=",")
#sPoints, vPoints = xPointstovPoints(xPoints)
#vFunc = vPointstovFunc(sPoints, vPoints)

#sVals = np.arange(0, sPoints[-1], 10)
#vVals = vFunc(sVals)
#plt.plot(sPoints, vPoints, 'o', sVals, vVals, '-')
#plt.show()




