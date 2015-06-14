import comfort as cmft
import interpolation as intrp
import math
import time

def Coeffs_to_VelAccel(a, s, t):
   t0 = time.time()
   da = [[j * quintic[j+1] for j in range(5)] for quintic in a]
   t1 = time.time()
#   print "Computing coefficients of 1st derivative took " +str(t1-t0) +" seconds."
   d2a = [[j * quartic[j+1] for j in range(4)] for quartic in da]
   t2 = time.time()
#   print "Computing coefficients of 2nd derivative took " +str(t2-t1) +" seconds."
   v = [intrp.Coeffs_to_Vals(da, five_minute_interval, t) for five_minute_interval in s]
   A = [intrp.Coeffs_to_Vals(d2a, five_minute_interval, t) for five_minute_interval in s]
   t3 = time.time()
   print "Evaluating both 1st and 2nd derivatives took " + str(t3-t2) + " seconds."
   return [v, A]

def comfort_and_Triptime(tht_i_phi_i):
   #Input is waypoints in long-lat (in radians): tht_i_phi_i
   #Compute coefficients of piecewise quintic polynomial:
   print "Pulling coefficients of piecewise quintic polynomial..."
   ax, ay, az, t = intrp.Points_to_Coeffs(tht_i_phi_i, 4)

   # Form list "s" of sampling times:
   print "Forming list of sampling times..."
   Q = 2**8. # number of rectangles in the Riemann sum (for efficiency, keep this a power of two).
   L = int(math.floor(t[-1]/300))
   s = [[t[-1] * (i + j/Q)/L + .05 for j in range(int(Q))] for i in range(L)]

   # Sample velocity and acceleration at "s":
   print "Sampling velocity and acceleration at these times..."
   print "Sampling the x-component..."
   vx, Ax = Coeffs_to_VelAccel(ax, s, t)
   print "Sampling the y-component..."
   vy, Ay = Coeffs_to_VelAccel(ay, s, t)
   print "Sampling the z-component..."
   vz, Az = Coeffs_to_VelAccel(az, s, t)
   v = [zip(vx[i], vy[i], vz[i]) for i in range(len(vx))]
   a = [zip(Ax[i], Ay[i], Az[i]) for i in range(len(Ax))]

   #Output is comfort rating and triptime:
   T = t[-1] / L
   mu = 1
   print "Computing comfort rating of sampled data..."
   comfort_Ratings = [cmft.comfort(v[i], a[i], T, mu) for i in range(len(v))]
   comfort = max(comfort_Ratings)
   triptime = t[-1]
   return [comfort, triptime]

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
