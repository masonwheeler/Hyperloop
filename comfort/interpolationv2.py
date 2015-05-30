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
	b = [0]*(N+1)
	b[0] = 6 * s[0]
	b[-1] = -6 * s[-1]
	for i in range(1,N):
		b[i] = 6 * (s[i] - s[i-1])
	A = [([0]*(N+1)) for i in range(N+1)]
	A[0][0] = 2 * h[0]
	A[-1][-1] = 2 * h[-1]
	A[0][1] = h[0]
	A[-1][-2] = h[-1]
	for i in range(1, N):
		A[i][i] = 2 * (h[i-1] + h[i])
		A[i][i-1] = h[i-1]
		A[i][i+1] = h[i]
	A = np.array(A)
	b = np.array(b)
	m = np.linalg.solve(A,b).tolist()
	a = [([0] * 4) for i in range(N)]
	for i in range(N):
		a[i][0] = y[i]
		a[i][1] = s[i] - h[i] * m[i]/2 - h[i] * (m[i+1] - m[i])/6
		a[i][2] = m[i]/2
		a[i][3] =  (m[i+1] - m[i])/(6 * h[i])
	return [a, x] 


def eval_polynomial(x, a, x_i):
	condlist = [(x_i[j] < x)*(x<x_i[j+1]) for j in range(len(x_i)-2)]
	def f(k):
		return lambda x: sum([a[k][j] * (x - x_i[k])**j for j in range(4)])
	funclist = [f(k) for k in range(len(a))]
	return np.piecewise(x, condlist, funclist)



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




start_time = time.time()
g_tol = .5 * 9.81
start_vel = 340
waypoints_spherical_deg = [
[-118.542569121974,34.39180314594903],
[-118.5545321592576,34.40532560522175],
[-118.5726782085907,34.42573843377703],
[-118.588806279766,34.43246046885258],
[-118.6127804458115,34.45237513675877],
[-118.6144358771204,34.47380623839012],
[-118.6212564796037,34.49095944887284],
[-118.6331899475494,34.51309927611657],
[-118.6774002503572,34.55924454709691],
[-118.7096804992186,34.58604135082059],
[-118.7426694608903,34.63241424132433],
[-118.7530926999706,34.65317552437557], 
[-118.7800247763688,34.68104965486667],
[-118.7955193340742,34.7028802312189],
[-118.8134599623722,34.72396607524714],
[-118.8344722241956,34.7551438114581],
[-118.8668964617316,34.79224217738597]]
waypoints_spherical = [[2*math.pi*point[0]/360,2*math.pi*point[1]/360] for point in waypoints_spherical_deg]
N = len(waypoints_spherical)
p = r_i(waypoints_spherical)
r = [radius(p[(i-1):(i+2)]) for i in range(1, N-1)]
v = [start_vel] + [min([math.sqrt(r[i]*g_tol),340]) for i in range(1,N-2)]+[start_vel]
t = t_i(v, p)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
  
polynomial = xyz_cubic_spline(waypoints_spherical, g_tol, start_vel)  
x_poly = polynomial[0]
y_poly = polynomial[1]
z_poly = polynomial[2]

t_plot = np.linspace(t[1]+.1, t[-2], 500)

x = eval_polynomial(t_plot, x_poly[0], x_poly[1])
y = eval_polynomial(t_plot, y_poly[0], y_poly[1])
z = eval_polynomial(t_plot, z_poly[0], z_poly[1])
ax.scatter(x, y, z,c='b',marker='+')

p = r_i(waypoints_spherical)
x_i = [point[0] for point in p]
y_i = [point[1] for point in p]
z_i = [point[2] for point in p]
ax.scatter(x_i, y_i, z_i, c='r', marker='o')
    
ax.set_xlabel(r'$x(t)$')
ax.set_ylabel(r'$y(t)$')
ax.set_zlabel(r'$z(t)$')   
plt.title('Cubic-Spline Interpolation (LA-SF)')
plt.grid(True)
print("Task completed in  %s seconds" % (time.time() - start_time))

plt.show()









