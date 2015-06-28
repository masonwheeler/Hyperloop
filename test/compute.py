import comfort as cmft
import interpolation as intrp
import numpy as np
import math
import time


def list_differentiate(List, dt):
  N = len(List)
  dList = [0]*N
  for i in range(1,N):
    dList[i] = (List[i+1]-List[i-1])/(2*dt)
  dList[0] = (List[1]-List[0])/dt
  dList[N-1] = (List[N-1]-List[N-2])/dt
  return dList


def Coeffs_to_VelAccel(a, s, t):
   da = [[j * quintic[j] for j in range(1,6)] for quintic in a]
   d2a = [[j * quartic[j] for j in range(1,5)] for quartic in da]
   print s[0]
   print intrp.Coeffs_to_Vals(da, s[0], t)
   v = [intrp.Coeffs_to_Vals(da, dosage_interval, t) for dosage_interval in s]
   A = [intrp.Coeffs_to_Vals(d2a, dosage_interval, t) for dosage_interval in s]
   return [v, A]

def comfortToActual(comfort_rating):
   if comfort_rating < 1:
     return "not noticeable"
   elif comfort_rating < 2:
     return "just noticeable"
   elif comfort_rating < 2.5:
     return "clearly noticeable"
   elif comfort_rating < 3:
     return "more pronounced but not unpleasant"
   elif comfort_rating < 3.25:
     return "strong, irregular, but still tolerable"
   elif comfort_rating < 3.5:
     return "very irregular"
   elif comfort_rating < 4:
     return "extremely irregular, unpleasant, annoying; prolonged exposure intolerable"
   else:
     return "extremely unpleasant; prolonged exposure harmful"


def fetch_Interpolation_Data(p, edges):
   #Input is waypoints in a chart: p
   #Compute coefficients of piecewise quintic polynomial:
   ax, ay, t = intrp.Points_to_Coeffs(p, 6)

   # Form list "s" of sampling times:
   N = len(p) - 1
   Q = 2**8. # number of rectangles in the Riemann sum (for efficiency, keep this a power of two).
   s = [[t[i] * (j/Q)*(t[i+1] - t[i]) + .05 for j in range(int(Q))] for i in range(N)]

  # h = [edge.heights for edge in edges]
  # dt = [times[1]-times[0] for times in s]
  # dh = [list_differentiate(heights, dt[i]) for i in range(len(h))]
  # d2h = [list_differentiate(dheights, dt[i]) for for i in range(len(h))]
   h = [[0]*len(sublist) for sublist in s]

   # Sample velocity and acceleration at "s":
   vx, Ax = Coeffs_to_VelAccel(ax, s, t)
   vy, Ay = Coeffs_to_VelAccel(ay, s, t)
   v = [zip(vx[i], vy[i], h) for i in range(len(vx))]
   a = [zip(Ax[i], Ay[i], h) for i in range(len(Ax))]   
   
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
   pts = zip(intrp.Coeffs_to_Vals(ax, plot_times, t), intrp.Coeffs_to_Vals(ay, plot_times, t), intrp.Coeffs_to_Vals(az, plot_times, t))
   vpts = [np.linalg.norm(vel_vector) for vel_vector in joined_v]
   apts = [np.linalg.norm(accel_vector) for accel_vector in joined_a]
   return [comfort_Ratings, triptime, plot_times, pts, vpts, apts]

# pointsDeg = [
# [-118.542569121974,34.39180314594903],
# [-118.5545321592576,34.40532560522175],
# [-118.5726782085907,34.42573843377703],
# [-118.588806279766,34.43246046885258],
# [-118.6127804458115,34.45237513675877],
# [-118.6144358771204,34.47380623839012],
# [-118.6212564796037,34.49095944887284],
# [-118.6331899475494,34.51309927611657],
# [-118.6774002503572,34.55924454709691],
# [-118.7096804992186,34.58604135082059],
# [-118.7426694608903,34.63241424132433],
# [-118.7530926999706,34.65317552437557], 
# [-118.7800247763688,34.68104965486667],
# [-118.7955193340742,34.7028802312189],
# [-118.8134599623722,34.72396607524714],
# [-118.8344722241956,34.7551438114581],
# [-118.8668964617316,34.79224217738597]]
# tht_i_phi_i = [[2*math.pi*point[0]/360,2*math.pi*point[1]/360] for point in pointsDeg]

# start_time = time.time()
# print comfort_and_Triptime(tht_i_phi_i)
# print("Task completed in  %s seconds" % (time.time() - start_time))
