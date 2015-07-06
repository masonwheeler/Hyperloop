import math
import numpy as np
import genVelocity as gen
import spatInterp as spat
import reParametrize as param

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

def fetch_Interpolation_Data(p, edges):
   #Input is waypoints in a chart: p
   #Compute coefficients of piecewise quintic polynomial:
   xPoints = np.genfromtxt('/Users/Droberts/Dropbox/The Hyperloop/keys/route2.csv', delimiter = ",")
   sPoints, vPoints = gen.xPointstovPoints(xPoints)
   vFunc = gen.vPointstovFunc(sPoints, vPoints)
   tPoints = np.arange(10,200.000001,(200-10.)/(len(xPoints)-1))
   xVals = np.transpose(spat.txPointstoxyVals(tPoints, xPoints, 7))
   sVals = xValstosVals(xVals)
   vVals = vFunctovVals(vFunc, sVals, sPoints)
   tVals = vValstotVals(sVals, vVals)
   vVals = [vVals[i-1]*(xVals[i]-xVals[i-1])/np.linalg.norm(xVals[i]-xVals[i-1]) for i in range(1,len(vVals))]+[[0,0]]
   aVals = np.transpose([ND(vVals[:][mu], tVals) for mu in [0,1]])
   
   h = [edge.heights for edge in edges]
   dt = [times[1]-times[0] for times in s]
   dh = [list_differentiate(heights, dt[i]) for i in range(len(h))]
   d2h = [list_differentiate(dheights, dt[i]) for for i in range(len(h))]

   # Sample velocity and acceleration at "s":
   vSamples = chunks(vVals, 127)
   aSamples = chunks(aVals, 127)
   v = [zip(v[i][0], v[i][1], dh[i]) for i in range(len(vSamples))]
   a = [zip(a[i][0], a[i][1], d2h[i]) for i in range(len(aSamples))]      


   #Output is comfort rating and triptime:
   T = [tPoints[i]-tPoints[i-1] for i in range(1,len(t))]
   mu = 1
   comfort_Ratings = [cmft.comfort(v[i], a[i], T[i], mu) for i in range(len(v))]
   triptime = tPoints[-1]   
   joined_a = sum(a,[])
   apts = [np.linalg.norm(accel_vector) for accel_vector in joined_a]
   return [comfort_Ratings, triptime, tVals, xVals, vVals, apts]
