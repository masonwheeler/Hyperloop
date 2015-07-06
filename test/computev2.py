import math
import numpy as np
import genVelocity as gen
import spatInterp as spat
import reParametrize as param

def ND(f, t):
  N = len(f)
  df = [0]*N
  for i in range(N):
    df[i] = 0.5*((f[i+1]-f[i])/(t[i+1]-t[i]))
  df[0] = (f[1]-f[0])/dt
  df[N-1] = (f[N-1]-f[N-2])/dt
  return df


def Coeffs_to_VelAccel(a, s, t):
   da = [[j * quintic[j] for j in range(1,6)] for quintic in a]
   d2a = [[j * quartic[j] for j in range(1,5)] for quartic in da]
   v = [intrp.Coeffs_to_Vals(da, dosage_interval, t) for dosage_interval in s]
   A = [intrp.Coeffs_to_Vals(d2a, dosage_interval, t) for dosage_interval in s]
   return [v, A]

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
  # h = [edge.heights for edge in edges]
  # dt = [times[1]-times[0] for times in s]
  # dh = [list_differentiate(heights, dt[i]) for i in range(len(h))]
  # d2h = [list_differentiate(dheights, dt[i]) for for i in range(len(h))]
   h = [[0]*len(sublist) for sublist in s]

   # Sample velocity and acceleration at "s":
   vx, Ax = Coeffs_to_VelAccel(ax, s, t)
   vy, Ay = Coeffs_to_VelAccel(ay, s, t)
   v = [zip(vx[i], vy[i], h[i]) for i in range(len(vx))]
   a = [zip(Ax[i], Ay[i], h[i]) for i in range(len(Ax))]      
  # v = [zip(vx[i], vy[i], dh[i]) for i in range(len(vx))]
  # a = [zip(Ax[i], Ay[i], d2h[i]) for i in range(len(Ax))]

   #Output is comfort rating and triptime:
   T = [t[i]-t[i-1] for i in range(1,len(t))]
   mu = 1
   comfort_Ratings = [cmft.comfort(v[i], a[i], T[i], mu) for i in range(len(v))]
   triptime = t[-1]   
   plot_times = sum(s,[])
   joined_v = sum(v,[])
   joined_a = sum(a,[])
   joined_h = sum(h,[])
   pts = zip(intrp.Coeffs_to_Vals(ax, plot_times, t), intrp.Coeffs_to_Vals(ay, plot_times, t))
   vpts = [np.linalg.norm(vel_vector) for vel_vector in joined_v]
   apts = [np.linalg.norm(accel_vector) for accel_vector in joined_a]
   return [comfort_Ratings, triptime, plot_times, pts, vpts, apts]
