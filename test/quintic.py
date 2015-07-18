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

def minimum_jerk_interpolation(data):
    t, x, dx0, d2x0, dxN, d2xN = data
    N = len(x)-1 #number of viapoints
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

def coeffs_to_vals(a, s, t_i):
    condlist = [(t_i[j] < s)*(s < t_i[j+1]) for j in range(len(t_i)-2)]
    def f(k):
        return lambda x: sum([a[k][j] * (x)**j for j in range(len(a[k]))])
    funclist = [f(k) for k in range(len(a))]
    return np.piecewise(s, condlist, funclist)
