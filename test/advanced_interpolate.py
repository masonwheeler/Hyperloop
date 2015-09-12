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



def gamma_matrix(t):
    gamma_matrix = np.array([[1, t, t**2, t**3, t**4, t**5],
                             [0, 1, 2 * t, 3 * t**2, 4 * t**3, 5 * t**4],
                             [0, 0, 2, 6 * t, 12 * t**2, 20 * t**3]])
    return gamma_matrix


def gamma_matrix_end(t):
    gamma_matrix_end = np.array([[1, t, t**2, t**3, t**4, t**5],
                                 [0, 1, 2 * t, 3 * t**2, 4 * t**3, 5 * t**4],
                                 [0, 0, 2, 6 * t, 12 * t**2, 20 * t**3],
                                 [0, 0, 0, 6, 24 * t, 60 * t**2],
                                 [0, 0, 0, 0, 24, 120 * t],
                                 [0, 0, 0, 0, 0, 0]])
    return gamma_matrix_end


def gamma_matrix_start(t):
    gamma_matrix_start = np.array([[0, 0, 0, 0, 0, 0],
                                   [0, -1, -2 * t, -3 * t**2, -4 * t**3, -5 * t**4],
                                   [0, 0, -2, -6 * t, -12 * t**2, -20 * t**3],
                                   [0, 0, 0, -6, -24 * t, -60 * t**2],
                                   [0, 0, 0, 0, -24, -120 * t],
                                   [1, t, t**2, t**3, t**4, t**5]])
    return gamma_matrix_start


def quint(t, x, dx0, dx_n):
    """ For an exposition of the quintic interpolation method see Polyakov (79.)
    """
    N = len(x) - 1  # number of viapoints
    d2x0 = d2x_n = 0
    b0 = np.array([x[0], dx0, d2x0])  # initial position and derivatives
    b_n = np.array([x[N], dx_n, d2x_n])  # final position and derivatives

    def bj(j):
        return np.array([x[j], 0, 0, 0, 0, x[j]])

    C = np.zeros((6 * N, 6 * N))
    b = np.zeros(6 * N)

    b[0:3] = b0
    b[6 * N - 3:6 * N] = b_n
    for j in range(1, N):
        b[3 + 6 * (j - 1):3 + 6 * j] = bj(j)

    C[0:3, 0:6] = gamma_matrix(t[0])
    C[6 * N - 3:6 * N, 6 * N - 6:6 * N] = gamma_matrix(t[N])
    for j in range(1, N):
        C[3 + 6 * (j - 1): 3 + 6 * j, 6 * (j - 1):6 * j] = gamma_matrix_end(t[j])
        C[3 + 6 * (j - 1): 3 + 6 * j, 6 * j:6 *(j + 1)] = gamma_matrix_start(t[j])

    a = np.linalg.solve(C, b)  # vector of polynomial coeffs (Polyakov A.3.1)
    alist = np.zeros((N, 6))
    for i in range(N):
        alist[i] = a[6 * i:6 * (i + 1)]
    list_of_coefficients = alist.tolist()
    return list_of_coefficients

def join_indices(N):
    if N <= 5:
        return []
    else:
        m, k = divmod(N, 5)
        if k >= 2:
            return [5 * j for j in range(1, m + 1)]
        else:
            return [5 * j for j in range(1, m)] + [int(5 * (m - 1) + np.ceil((5 + k) / 2.))]


def super_quint(t, x, M):
    """
    Extends quint() to allow for high numbers (> 5) of waypoints to be
    interpolated, without running into ill-conditioning problems.
    """

    J = join_indices(len(x) - 1)
    if len(J) == 0:
        polys = quint(t, x, 0, 0)
    else:
        u = [(x[j + 1] - x[j - 1]) / (t[j + 1] - t[j - 1]) for j in J]
        polys = quint(t[:J[0] + 1], x[:J[0] + 1], 0, u[0]) + sum([quint(t[J[i]:J[i + 1] + 1], x[J[i]:J[i + 1] + 1],
                                                                        u[i], u[i + 1]) for i in range(len(J) - 1)], []) + quint(t[J[-1]:], x[J[-1]:], u[-1], 0)

    t_m = [[t[i] + (m * 1. / M) * (t[i + 1] - t[i])
            for m in range(M)] for i in range(len(t) - 1)]
    x_m = [[np.dot(polys[i], [1, time, time**2, time**3, time**4, time**5])
            for time in t_m[i]] for i in range(len(t_m))]
    return [sum(t_m, []), sum(x_m, [])]


def para_super_q(x, M):
    """
    Extends super_quint to allow for an interpolation without an explicit
    parametrization a priori.
    This function is used to generate the spatial interpolation of each graph.
    """
    t = [15 * n for n in range(len(x))]
    x_points, y_points = np.transpose(x)
    t_m, x_m = super_quint(t, x_points, M)
    t_m, y_m = super_quint(t, y_points, M)
    return np.transpose([x_m, y_m])

def scipy_q(x, M):
    t = [15 * n for n in range(len(x))]
    t_m = sum([[t[i] + (m * 1. / M) * (t[i + 1] - t[i])
                for m in range(M)] for i in range(len(t) - 1)], [])

    x_points, y_points = np.transpose(x)
    x_func = UnivariateSpline(t, x_points, k=5)
    y_func = UnivariateSpline(t, y_points, k=5)

    x_m = x_func(t_m)
    y_m = y_func(t_m)
    return np.transpose([x_m, y_m])


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

# t_m = [[t[i]+(m/100.)*(t[i+1]-t[i]) for m in range(100)] for i in range(len(t)-1)]
# x_m = [[np.dot(polys[i],[1,time,time**2,time**3,time**4,time**5]) for time in t_m[i]] for i in range(len(t_m))]
# t_m = sum(t_m, [])
# x_m = sum(x_m, [])

# print "x_m is:"
# print x_m
# print "t_m is:"
# print t_m
# plt.plot(t_m, x_m, t, x)
# plt.show()


# Test join_indices(N):
# should get 5,5,5,3,3,...
# print [join_indices(n) for n in range(30)]


# Test super_quint(sp, vp, s, K):
# t_points = sorted(list(set([random.uniform(-100,100) for i in range(50)])))
# x_points = [random.uniform(-10,10) for i in range(len(t_points))]

# t, x = super_quint(t_points, x_points, 10)

# plt.plot(t, x, '.', t_points, x_points, 'o')
# plt.show()


# Test para_super_q(x, M):
#x_points = [random.uniform(-100,100) for i in range(40)]
#y_points = [random.uniform(-100,100) for i in range(40)]
#x = np.transpose([x_points, y_points])


# with open('/Users/Droberts/Dropbox/save/Dallas_to_Austin/Dallas_to_Austin_graphs/Dallas_to_Austin_graph003.csv', 'rb') as f:
#     reader = csv.reader(f)
#     x = list(reader)
# x = [[float(p[0]),float(p[1])] for p in x]
# x_points, y_points = np.transpose(x)

#x_vals = scipy_q(x, 100)
#x_vals, y_vals = np.transpose(x_vals)

#plt.plot(x_vals, y_vals, '.', x_points, y_points, 'o')
# plt.show()
