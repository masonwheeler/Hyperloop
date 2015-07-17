"""
Original Developer: David Roberts
Purpose of Module: To determine the boundary conditions which are
                   passed to the minimum jerk interpolation method.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify naming and remove unnecessary imports.
"""

#Standard Modules:
import math
import numpy as np

#Our Modules:
import radiusOfCurvature as rad

def radius_of_curv_to_max_vel(radiusOfCurvature):
  	return math.sqrt(radiusOfCurvature*.5*9.81)

def viapoints_to_times_and_maxvelocities(viapoints):
    numViapoints = len(viapoints)-1
    radiiOfCurvature = [rad.radius(viapoints[(i - 1):(i + 2)])
                        for i in range(1, numViaPoints-1)]
    maxVelocities = ([150] +
    [min([sum(map(radius_of_curv_to_max_vel,radiiOfCurvature[i:i+8]))/8, 330])
    for i in range(0, numViapoints - 9)]
    + [330,330,330,330,330,330,250,150])
    # replaced the following with the sum and map operators above
    #  + [min([(rv(r[i]) + rv(r[i+1]) + rv(r[i+2]) + rv(r[i+3])+ rv(r[i+4]) +
    #     rv(r[i+5]) + rv(r[i+6]) + rv(r[i+7]))/8, 330]) for i in range(0,N-9)]
    
    viapointTimes = rad.viapoint_times(maxVelocities, viapoints)
    return [viapointTimes, maxVelocities]

def process(viapointTimes, viapoints, maxVelocities, n, mu):
    N = len(p) - 1
    def u(i):
        u_unnormalized = np.subtract(np.array(p[i+1]),np.array(p[i]))
        u_normalized = u_unnormalized / np.linalg.norm(u_unnormalized)
        return u_normalized.tolist()
    m = int(math.ceil((N+0.0) / (n+0.0)))
    G = [[0]*6 for i in range(m)]
    x = [point[mu] for point in p]
    if m == 1:
        G = [[t,p,0,0,0,0]]
    elif m == 2:
        G[0] = [t[0:n+1],x[0:n+1],0,0,v[n]* u(n)[mu],0]
        G[1] = [t[n:N+1],x[n:N+1], v[n] *u(n)[mu],0,0,0]
    else:
        G[0] = [t[0:n+1],x[0:n+1],0,0,v[n] *u(n)[mu],0]
        for j in range(1,m-1):
          G[j] = [t[j*n:(j+1)*n+1], x[j*n:(j+1)*n+1], v[j*n]*u(j*n)[mu],0,v[(j+1)*n]*u((j+1)*n)[mu],0]
        G[-1] = [t[(m-1)*n:N+1],x[(m-1)*n:N+1], v[(m-1)*n]* u((m-1)*n)[mu],0,0,0]
    return G






