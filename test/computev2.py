"""
Original Developer: David Roberts
Purpose of Module: To generate a route from a graph.
Last Modified: 7/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To make compatible with graph modifications.
"""

#Standard Modules:
import math
import numpy as np
import csv
import matplotlib.pyplot as plt


#Our Modules
import genVelocityv2 as gen
import spatialinterpolation as spat
import reparametrize as param
import config
import build_pylons

class Route:
    cost = 0
    times = []
    points = []
    vPoints = []
    aPoints = []
    comfort = []

    def __init__(self, cost, times, points, vPoints, aPoints, comfort):
        self.cost = cost
        self.times = times
        self.points = points,
        self.vPoints = vPoints
        self.aPoints = aPoints
        self.comfort = comfort

    def display(self):     
        print("The route cost is: " + str(self.cost) + ".")
        print("The route times are: " + str(self.times) + ".")        
        print("The route points are: " + str(self.points) + ".")
        print("The route velocity points are: " + str(self.vPoints) + ".")        
        print("The route acceleration points are: " + str(self.aPoints) + ".")
        print("The route comfort is: " + str(self.comfort) + ".")


def ND(f, t):
    N = len(f)
    df = [0]*N
    for i in range(1,N-1):
        df[i] = 0.5*((f[i+1]-f[i])/(t[i+1]-t[i])+(f[i]-f[i-1])/(t[i]-t[i-1]))
    df[0] = (f[1]-f[0])/(t[1]-t[0])
    df[N-1] = (f[N-1]-f[N-2])/(t[N-1]-t[N-2])
    return df

def chunks(l, n):
    n = max(1, n)
    chunks = [l[i:i + n] for i in range(0, len(l), n)]
    return chunks

def graph_to_route(xPoints):
#    xPoints = graph.geospatials
    tPoints = np.arange(10,200.000001,(200-10.)/(len(xPoints)-1))
    xVals = np.transpose(spat.txPointstoxyVals(tPoints, xPoints, 7))
    sVals, vVals, vmaxvals = gen.vPoints(xVals)
    sVals, zVals, pylonElevations = build_pylons.build_pylons(sVals, xVals)
    points = [(xVals[i][0],xVals[i][1],zVals[i]) for i in range(len(xVals))]
    tVals = param.vValstotVals(sVals, vVals)
    vVals = [vVals[i-1]*(points[i]-points[i-1])/np.linalg.norm(points[i]-points[i-1]) for i in range(1,len(vVals))]+[[0,0]]
    aVals = np.transpose([ND(vVals[:][mu], tVals) for mu in [0,1,2]])
    
    plt.plot(sVals, vVals, sVals, vmaxvals)
    plt.show()

    plt.plot(sVals, zVals, sVals, pylonElevations)
    plt.show()

    # Sample velocity and acceleration at "s":   
    vSamples = chunks(vVals, config.numHeights)
    aSamples = chunks(aVals, config.numHeights)

    #Output is comfort rating and triptime:
    T = [tPoints[i]-tPoints[i-1] for i in range(1,len(t))]
    mu = 1
    comfort = [cmft.comfort(vSamples[i], aSamples[i], T[i], mu) for i in range(len(vSamples))]
    cost = 0  #    cost = graph.landCost + graph.pylonCost
    return Route(cost, tVals, points, vVals, aVals, comfort)



with open('graph001.csv', 'rb') as f:
    reader = csv.reader(f)
    xPoints = list(reader)

xPoints = [[float(xPoint[0]),float(xPoint[1])] for xPoint in xPoints]
graph_to_route(xPoints)




