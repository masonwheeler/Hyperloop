"""
Original Developer: David Roberts
Purpose of Module: To generate continuous data from a discrete route.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify naming.
"""


import math
import numpy as np
import velocityprofile 
import spatInterp as spat
import reParametrize as param
import config

class fullRoute:
    cost = 0
    times = []
    points = []
    v_points = []
    a_points = []
    comfort = []

    def __init__(self, cost,
                 times, points, v_points, a_points, comfort):
        self.cost = cost
        self.times = times
        self.points = points,
        self.v_points = v_points
        self.a_points = a_points
        self.comfort = comfort

    def display(self):     
        print("The route cost is: " + str(self.cost) + ".")
        print("The route times are: " + str(self.times) + ".")        
        print("The route points are: " + str(self.points) + ".")
        print("The route velocity points are: " + str(self.v_points) + ".")        
        print("The route acceleration points are: " + str(self.a_points) + ".")
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
    return [l[i:i + n] for i in range(0, len(l), n)]

def route_to_fullRoute(route):
   xPoints = route.xyCoords
   sPoints, vPoints = velocityprofile.xPointstovPoints(xPoints)
   vFunc = gen.vPointstovFunc(sPoints, vPoints)
   tPoints = np.arange(10,200.000001,(200-10.)/(len(xPoints)-1))
   xVals = np.transpose(spat.txPointstoxyVals(tPoints, xPoints, 7))
   sVals = xValstosVals(xVals)
   vVals = vFunctovVals(vFunc, sVals, sPoints)
   tVals = vValstotVals(sVals, vVals)
   vVals = [vVals[i-1]*(xVals[i]-xVals[i-1])/np.linalg.norm(xVals[i]-xVals[i-1]) for i in range(1,len(vVals))]+[[0,0]]
   aVals = np.transpose([ND(vVals[:][mu], tVals) for mu in [0,1]])
   
   Edges = route.edges
   h = [edge.heights for edge in Edges]
   dt = [times[1]-times[0] for times in s]
   dh = [list_differentiate(heights, dt[i]) for i in range(len(h))]
   d2h = [list_differentiate(dheights, dt[i]) for i in range(len(h))]

   # Sample velocity and acceleration at "s":
   
   vSamples = chunks(vVals, config.numHeights)
   aSamples = chunks(aVals, config.numHeights)
   v = [zip(v[i][0], v[i][1], dh[i]) for i in range(len(vSamples))]
   a = [zip(a[i][0], a[i][1], d2h[i]) for i in range(len(aSamples))]      


   #Output is comfort rating and triptime:
   T = [tPoints[i]-tPoints[i-1] for i in range(1,len(t))]
   mu = 1
   comfort = [cmft.comfort(v[i], a[i], T[i], mu) for i in range(len(v))]
   times = tVals
   joined_a = sum(a,[])
   a_points = [np.linalg.norm(accel_vector) for accel_vector in joined_a]
   v_points = vVals
   cost = route.cost
   points = xVals
   return fullRoute(cost, times, points, v_points, a_points, comfort)
