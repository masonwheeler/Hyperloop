import math
import numpy as np


def list_differentiate(List, dt):
	N = len(List)
	dList = [0]*N
	for i in range(1,N):
		dList[i] = (List[i+1]-List[i-1])/(2*dt)
	dList[0] = (List[1]-List[0])/dt
	dList[N-1] = (List[N-1]-List[N-2])/dt
	return dList

def interpolation_data(p, edges):
   N = len(p) - 1
   Q = 2**8. # number of rectangles in the Riemann sum (for efficiency, keep this a power of two).
   s = [[t[i] * (j/Q)*(t[i+1] - t[i]) + .05 for j in range(int(Q))] for i in range(N + 1)]



   vx, Ax = Coeffs_to_VelAccel(ax, s, t)
   vy, Ay = Coeffs_to_VelAccel(ay, s, t)

   h = [edge.heights for edge in edges]
   dt = [times[1]-times[0] for times in s]
   dh = [list_differentiate(heights, dt[i]) for i in range(len(h))]
   d2h = [list_differentiate(dheights, dt[i]) for for i in range(len(h))]

   v = [zip(vx[i], vy[i], dh[i]) for i in range(len(vx))]
   a = [zip(Ax[i], Ay[i], d2h[i]) for i in range(len(Ax))]
