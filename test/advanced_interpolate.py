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
import random
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import csv

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
    if N <= 5:
        return []
    else:
        m, k = divmod(N, 5)
        if k >= 2:
            return [5*j for j in range(1,m+1)]
        else: 
            return [5*j for j in range(1,m)] + [int(5*(m-1)+np.ceil((5+k)/2.))]


def superQuint(t, x, M):
    J = joinIndices(len(x)-1)
    if len(J) == 0:
        polys = quint(t,x,0,0)
    else:
        u = [(x[j+1]-x[j-1])/(t[j+1]-t[j-1]) for j in J]
        polys = quint(t[:J[0]+1],x[:J[0]+1],0,u[0]) + sum([quint(t[J[i]:J[i+1]+1],x[J[i]:J[i+1]+1],u[i],u[i+1]) for i in range(len(J)-1)],[]) + quint(t[J[-1]:],x[J[-1]:],u[-1],0)

    tM = [[t[i]+(m*1./M)*(t[i+1]-t[i]) for m in range(M)] for i in range(len(t)-1)]
    xM = [[np.dot(polys[i],[1,time,time**2,time**3,time**4,time**5]) for time in tM[i]] for i in range(len(tM))]
    return [sum(tM, []), sum(xM, [])]


# paraSuperQ(): Extends superQuint() to allow for an interpolation without an explicit parametrization a priori:
# this function is used to generate the spatial interpolation of each graph.

def paraSuperQ(x, M):
    t = [15*n for n in range(len(x))]
    xPoints, yPoints = np.transpose(x)
    tM, xM = superQuint(t, xPoints, M)
    tM, yM = superQuint(t, yPoints, M)
    return np.transpose([xM, yM])



# Standard interpolate function from scipy is imported here as a benchmark.

def scipyQ(x, M):
    t = [15*n for n in range(len(x))]
    tM = sum([[t[i]+(m*1./M)*(t[i+1]-t[i]) for m in range(M)] for i in range(len(t)-1)], [])

    xPoints, yPoints = np.transpose(x)
    xFunc = UnivariateSpline(t, xPoints, k=5)
    yFunc = UnivariateSpline(t, yPoints, k=5)
    
    xM = xFunc(tM)
    yM = yFunc(tM)
    return np.transpose([xM, yM])



# Test quint(t, x, v1, v2):

# t = [i for i in range(6)]
# x = [random.uniform(-10,10) for i in range(len(t))]
# v1 = random.uniform(-10,10)
# v2 = random.uniform(-10,10)
# print "x is:"
# print x
# print "t is:"
# print t
# print "(v1, v2) is:"
# print [v1, v2]

# polys = quint(t, x, v1, v2)

# tM = [[t[i]+(m/100.)*(t[i+1]-t[i]) for m in range(100)] for i in range(len(t)-1)]
# xM = [[np.dot(polys[i],[1,time,time**2,time**3,time**4,time**5]) for time in tM[i]] for i in range(len(tM))]
# tM = sum(tM, [])
# xM = sum(xM, [])

# print "xM is:"
# print xM
# print "tM is:"
# print tM
# plt.plot(tM, xM, t, x)
# plt.show()


# Test joinIndices(N):
# should get 5,5,5,3,3,...
# print [joinIndices(n) for n in range(30)]



# Test superQuint(sp, vp, s, K):
# tPoints = sorted(list(set([random.uniform(-100,100) for i in range(50)])))
# xPoints = [random.uniform(-10,10) for i in range(len(tPoints))]

# t, x = superQuint(tPoints, xPoints, 10)

# plt.plot(t, x, '.', tPoints, xPoints, 'o')
# plt.show()


# Test paraSuperQ(x, M):
xPoints = [random.uniform(-100,100) for i in range(40)]
yPoints = [random.uniform(-100,100) for i in range(40)]
x = np.transpose([xPoints, yPoints])


# with open('/Users/Droberts/Dropbox/save/Dallas_to_Austin/Dallas_to_Austin_graphs/Dallas_to_Austin_graph003.csv', 'rb') as f:
#     reader = csv.reader(f)
#     x = list(reader)
# x = [[float(p[0]),float(p[1])] for p in x]
# xPoints, yPoints = np.transpose(x)

xVals = scipyQ(x, 100)
xVals, yVals = np.transpose(xVals)

plt.plot(xVals, yVals, '.', xPoints, yPoints, 'o')
plt.show()





