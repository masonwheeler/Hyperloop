"""
Original Developer: David Roberts
Purpose of Module: Takes in velocity profile and reparametrizes
                   route with respect to time.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To fix formatting.
"""

#Standard Modules:
import math
import numpy as np

#Our Modules:
import util


def vValstotVals(sVals, vVals):
    tVals = [0] * len(vVals)
    tVals[1] = (sVals[1] - sVals[0]) / gen.mean(vVals[0:2])
    for i in range(2, len(vVals)):
        tVals[i] = tVals[i-1] + (sVals[i] - sVals[i-1]) / vVals[i-1]
    tVals[-1] = (sVals[-1] - sVals[-2]) / util.mean(vVals[-2:len(vVals)])
    return tVals

def xValstosVals(xVals):
    sVals = [0] * len(xVals)
    for i in range(1, len(xVals)):
        sVals[i] = sVals[i-1] + np.linalg.norm(xVals[i] - xVals[i-1])
    return sVals

def vFunctovVals(vFunc, sVals, sPoints):
    sVals = np.array(sVals)
    S = sPoints[-1]
    Sprime = sVals[-1]
    vVals = vFunc(sVals * (S / Sprime))
    return vVals

# start = time.time()
# xPoints = np.genfromtxt('/Users/Droberts/Dropbox/The Hyperloop/keys/route2.csv', delimiter = ",")
# sPoints, vPoints = gen.xPointstovPoints(xPoints)
# vFunc = gen.vPointstovFunc(sPoints, vPoints)
# tPoints = np.arange(10,200.000001,(200-10.)/(len(xPoints)-1))
# xVals = np.transpose(spat.txPointstoxyVals(tPoints, xPoints, 7))
# sVals = xValstosVals(xVals)
# vVals = vFunctovVals(vFunc, sVals, sPoints)
# tVals = vValstotVals(sVals, vVals)
# print tVals
# print time.time()-start



