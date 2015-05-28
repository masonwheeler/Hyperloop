import math
import numpy as np
import time
import scipy
import scipy.interpolate
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

R =  6.371*(10**6)

def radius(three_points):
	p1, p2, p3 = three_points
	a = np.linalg.norm(np.subtract(p1, p2))
	b = np.linalg.norm(np.subtract(p2, p3))
	c = np.linalg.norm(np.subtract(p1, p3))
	p = (a + b + c) / 2
	A = math.sqrt(p * (p - a) * (p - b) * (p - c))
	if A == 0:
		return 1000000000000
	else:
		return a * b * c / (4 * A)

def r_i(coordinates):
    r_i_results = []
    for coordinate in coordinates:
        x_i = R*math.cos(coordinate[0])*math.cos(coordinate[1])
        y_i = R*math.cos(coordinate[0])*math.sin(coordinate[1])
        z_i = R*math.sin(coordinate[0])
        r_i_results.append([x_i, y_i, z_i])
    return r_i_results

def t_i(v_i, r_i):
    t_i_results = [0]
    for i in range(len(v_i)):
        t_i = t_i_results[i] + np.linalg.norm(np.subtract(r_i[i+1], r_i[i])) / v_i[i]
        t_i_results.append(t_i)
    return t_i_results    

def interpolate_spline(x, y):
	N = len(x) - 1
	h = [x[i+1] - x[i] for i in range(N)]
	s = [(y[i+1] - y[i]) / h[i] for i in range(N)]
	b = [0]*(N)
	b[0] = 6 * s[0]
	b[-1] = -6 * s[-1]
	for i in range(N):
		b[i] = 6 * (s[i] - s[i-1])
	A = ([0]*(N+1)) * (N+1)
	A[0][0] = 2 * h[0]
	A[-1][-1] = 2 * h[-1]
	for i in range(N-1):
		A[i][i] = 2 * (h[i-1] + h[i])
		A[i][i-1] = h[i-1]
		A[i-1][i] = h[i-1]
	A = np.array(A)
	b = np.array(b)
	m = np.linalg.solve(A,b).tolist()
	a = ([0] * 4) * N
	for i in range(N+1):
		a[i][0] = y[i]
		a[i][1] = s[i] - h[i] * m[i]/2 - h[i] * (m[i+1] - m[i])/6
		a[i][2] = m[i]/2
		a[i][3] =  (m[i+1] - m[i])/(6 * h[i])
	return [a, x] 

def coeffs_to_polynomial(coeffs):
	def f(x): 
		return sum([coeffs[i] * (x - y)])
	return f


def xyz_cubic_spline(waypoints_spherical, g_tol,start_vel):
	N = len(waypoints_spherical)
	p = r_i(waypoints_spherical)
	r = [radius(p[(i - 1):(i + 2)]) for i in range(1, N-1)]
	v = [start_vel] + [math.sqrt(Radius*g_tol) for Radius in r]
	t = t_i(v, p)
	x = [point[0] for point in p]
	y = [point[1] for point in p]
	z = [point[2] for point in p]
	return [interpolate_spline(t, x), interpolate_spline(t, y), interpolate_spline(t, z)]






