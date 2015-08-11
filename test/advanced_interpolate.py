"""
Original Developer: David Roberts
Purpose of Module: To provide an implementation of the minimum jerk
                   implementation described in Polyakov.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify naming and add citations.
Citations:
  "Analysis of Monkey Scribbles During Learning in the Framework of
   Models of Planar Hand Motion"
    - Polyakov
"""

import math
import numpy as np

"""
For an exposition of the following see (Polyakov page 79).
"""

def gamma_matrix(t):
    gammaMatrix = np.array([[1, t, t**2, t**3, t**4, t**5], 
                      [0, 1, 2*t, 3*t**2, 4*t**3, 5*t**4],
                      [0, 0, 2, 6*t, 12*t**2, 20*t**3]])
    return gammaMatrix

def gamma_matrix_end(t):
    gammaMatrixEnd = np.array([[1, t, t**2, t**3, t**4, t**5], 
                        [0, 1, 2*t, 3*t**2, 4*t**3, 5*t**4],
                        [0, 0, 2, 6*t, 12*t**2, 20*t**3],
                        [0, 0, 0, 6, 24*t, 60*t**2],
                        [0, 0, 0, 0, 24, 120*t],
                        [0, 0, 0, 0, 0, 0]])
    return gammaMatrixEnd 

def gamma_matrix_start(t):
    gammaMatrixStart = np.array([[0, 0, 0, 0, 0, 0], 
                                 [0, -1, -2*t, -3*t**2, -4*t**3, -5*t**4],
                                 [0, 0, -2, -6*t, -12*t**2, -20*t**3],
                                 [0, 0, 0, -6, -24*t, -60*t**2],
                                 [0, 0, 0, 0, -24, -120*t],
                                 [1, t, t**2, t**3, t**4, t**5]])
    return gammaMatrixStart

def quint(t, x, dx0, dxN):
    N = len(x)-1 #number of viapoints
    d2x0 = d2xN = 0
    b0 = np.array([x[0], dx0, d2x0]) #initial position and derivatives
    bN = np.array([x[N], dxN, d2xN]) #final position and derivatives
    def bj(j): 
        return np.array([x[j], 0, 0, 0, 0, x[j]]) 

    C = np.zeros((6*N, 6*N))
    b = np.zeros(6*N)

    b[0:3] = b0
    b[6*N - 3 :6*N] = bN
    for j in range(1, N):
        b[3 + 6*(j-1):3 + 6*j] = bj(j)

    C[0:3,0:6] = gamma_matrix(t[0])
    C[6*N - 3:6*N, 6*N - 6:6*N] = gamma_matrix(t[N])
    for j in range(1, N):
        C[3 + 6*(j-1) : 3 + 6*j,6*(j-1):6*j] = gamma_matrix_end(t[j])
        C[3 + 6*(j-1) : 3 + 6*j,6*j:6*(j+1)] = gamma_matrix_start(t[j])

    a = np.linalg.solve(C,b) #vector of polynomial coeffs (Polyakov A.3.1)
    alist = np.zeros((N, 6))
    for i in range(N):
        alist[i] = a[6*i:6*(i+1)]
    listOfCoefficients = alist.tolist()
    return listOfCoefficients

# superQuint(): Extends quint() to allow for high numbers (> 5) of waypoints to be interpolated, 
# without running into ill-conditioning problems:

def joinIndices(N):
    m, k = divmod(N, 5)
    if m >= 2:
        return [5*j for j in range(m+1)]
    else: 
        return [5*j for j in range(m)] + [int(5*(m-1)+np.ceil((5+m)/2))]


def superQuint(sInterp, zInterp, s, K):
    J = joinIndices(len(zInterp)-1)
    if len(J) == 0:
        polys = quint(sInterp[:j[0]+1],zInterp[:j[0]+1],0,0)
    else:
        u = [(zInterp[j+1]-zInterp[j-1])/(sInterp[j+1]-sInterp[j-1]) for j in J]
        polys = [quint(sInterp[:j[0]+1],zInterp[:j[0]+1],0,u[0])]\
            + sum([quint(sInterp[j[i]:j[i+1]+1],zInterp[j[i]:j[i+1]+1],u[i],u[i+1]) for i in range(1,len(J)-1)])
            + [quint(sInterp[j[-1]:],zInterp[j[-1]:],u[-1],0)]
    sM = [[s[i] for i in range(K[j],K[j+1])] for j in range(len(K)-1)]
    zM = [[np.dot(polys[i],[1,dist,dist**2,dist**3,dist**4,dist**5]) for time in sM[i]]\
             for i in range(len(sM))]
    return [sum(sM), sum(zM)]


# paraSuperQ(): Extends superQuint() to allow for an interpolation without an explicit parametrization a priori:
# this function is used to generate the spatial interpolation of each graph.

def paraSuperQ(x, M):
    t = [15*n for n in range(len(x))]
    xPoints, yPoints = np.transpose(x)
    tM = sum([[t[i]+(m/M)*(t[i+1]-t[i]) for m in range(M)] for i in range(len(t)-1)])
    K = [i*M for i in range(len(t))]
    xM = superQuint(t, xPoints, tM, K)
    yM = superQuint(t, yPoints, tM, K)
    return np.transpose([xM, yM])

t = [i for i in range(30)]
x = [i**2-10*i for i in range(30)]
print "x is:"
print x
print "t is:"
print t
superQuint(x, 200)






