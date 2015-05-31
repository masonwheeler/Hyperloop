import math
import numpy as np
import time
import scipy
import scipy.interpolate
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import radiusOfCurvature as rad

def Gamma(t):
	return np.array([[1, t, t**2, t**3, t**4, t**5], 
		[0, 1, 2*t, 3*t**2, 4*t**3, 5*t**4],
		[0, 0, 2, 6*t, 12*t**2, 20*t**3]])

def GammaEn(t):
	return np.array([[1, t, t**2, t**3, t**4, t**5], 
		[0, 1, 2*t, 3*t**2, 4*t**3, 5*t**4],
		[0, 0, 2, 6*t, 12*t**2, 20*t**3],
		[0, 0, 0, 6, 24*t, 60*t**2],
		[0, 0, 0, 0, 24, 120*t],
		[0, 0, 0, 0, 0, 0]])

def GammaSt(t):
	return np.array([[0, 0, 0, 0, 0, 0], 
		[0, -1, -2*t, -3*t**2, -4*t**3, -5*t**4],
		[0, 0, -2, -6*t, -12*t**2, -20*t**3],
		[0, 0, 0, -6, -24*t, -60*t**2],
		[0, 0, 0, 0, -24, -120*t],
		[1, t, t**2, t**3, t**4, t**5]])


def interpolate_quintic(t, x, dx0, d2x0, dxN, d2xN):
	N = len(x)-1
	b0 = np.array([x[0], dx0, d2x0])
	bN = np.array([x[N], dxN, d2xN])
	def bj(j):
		return np.array([x[j], 0, 0, 0, 0, x[j]])
	C = np.zeros((6*N, 6*N))
	b = np.zeros(6*N)
	b[0:3] = b0
	b[6*N - 3 :6*N] = bN
	for j in range(1, N):
		b[3 + 6*(j-1):3 + 6*j] = bj(j)
	C[0:3,0:6] = Gamma(t[0])
	C[6*N - 3:6*N, 6*N - 6:6*N] = Gamma(t[N])
	for j in range(1, N):
		C[3 + 6*(j-1) : 3 + 6*j,6*(j-1):6*j] = GammaEn(t[j])
		C[3 + 6*(j-1) : 3 + 6*j,6*j:6*(j+1)] = GammaSt(t[j])
	a = np.linalg.solve(C,b)
	alist = np.zeros((N, 6))
	for i in range(N):
		alist[i] = a[6*i:6*(i+1)]
	return alist.tolist()


def eval_polynomial(x, a, x_i):
	condlist = [(x_i[j] < x)*(x<x_i[j+1]) for j in range(len(x_i)-2)]
	def f(k):
		return lambda x: sum([a[k][j] * (x)**j for j in range(6)])
	funclist = [f(k) for k in range(len(a))]
	return np.piecewise(x, condlist, funclist)



def xyz_quintic(waypoints_spherical, g_tol,start_vel, n):
	N = len(waypoints_spherical)
	p = rad.r_i(waypoints_spherical)
	r = [rad.radius(p[(i - 1):(i + 2)]) for i in range(1, N-1)]
	v = [start_vel] + [min([math.sqrt(Radius*g_tol),340]) for Radius in r]
	print v
	t = rad.t_i(v, p)
	x = [point[0] for point in p]
#	y = [point[1] for point in p]
#	z = [point[2] for point in p]
	def u(i):
		u_unnormalized = np.subtract(np.array(p[i+1]),np.array(p[i]))
		u_normalized = u_unnormalized / np.linalg.norm(u_unnormalized)
		return u_normalized.tolist()
	m = int(math.ceil((N+0.0) / (n+0.0)))
	if m == 1:
		ax = interpolate_quintic(t[0:N+1], x[0:N+1], 0,0,0,0)
#		ay = interpolate_quintic(t[0:n+1], y[0:n+1], 0,0,0,0)
#		az = interpolate_quintic(t[0:n+1], z[0:n+1], 0,0,0,0)
	elif m == 2:
		ax = interpolate_quintic(t[0:n+1], x[0:n+1], 0,0,v[n]*u(n)[0],0)
		ax += interpolate_quintic(t[n:N+1], x[n:N+1], v[n]*u(n)[0],0,0,0)
#		ay = interpolate_quintic(t[0:n+1], y[0:n+1], 0,0,v[n]*u(n)[1],0)
#		ay += interpolate_quintic(t[n:N+1], y[n:N+1], v[n]*u(n)[1],0,0,0)
#		az = interpolate_quintic(t[0:n+1], z[0:n+1], 0,0,v[n]*u(n)[2],0)
#		az += interpolate_quintic(t[n:N+1], z[n:N+1], v[n]*u(n)[2],0,0,0)
	else: 
		ax = interpolate_quintic(t[0:n+1], x[0:n+1], 0,0,v[n]*u(n)[0],0)
		for j in range(1,m-1):
			ax += interpolate_quintic(t[j*n:(j+1)*n+1], x[j*n:(j+1)*n+1], v[j*n]*u(j*n)[0],0,v[(j+1)*n]*u((j+1)*n)[0],0)
		ax += interpolate_quintic(t[(m-1)*n:N+1], x[(m-1)*n:N+1], v[(m-1)*n]*u((m-1)*n)[0],0,0,0)
#		ay = interpolate_quintic(t[0:n+1], y[0:n+1], 0,0,v[n]*u(n)[1],0)
#		for j in range(1,m-1):
#			ay += interpolate_quintic(t[j*n:(j+1)*n+1], y[j*n:(j+1)*n], v[j*n]*u(j*n)[1],0,v[(j+1)*n]*u((j+1)*n)[1],0)
#		ay += interpolate_quintic(t[(m-1)*n:N+1], y[(m-1)*n:N+1], v[(m-1)*n]*u((m-1)*n)[1],0,0,0)
#		az = interpolate_quintic(t[0:n+1], z[0:n+1], 0,0,v[n]*u(n)[2],0)
#		for j in range(1,m-1):
#			az += interpolate_quintic(t[j*n:(j+1)*n+1], z[j*n:(j+1)*n+1], v[j*n]*u(j*n)[2],0,v[(j+1)*n]*u((j+1)*n)[2],0)
#		az += interpolate_quintic(t[(m-1)*n:N+1], z[(m-1)*n:N+1], v[(m-1)*n]*u((m-1)*n)[2],0,0,0)
	return ax#, ay, az]




start_time = time.time()
g_tol = .5 * 9.81
start_vel = 40
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
waypoints_spherical = [[2*math.pi*point[0]/360,2*math.pi*point[1]/360] for point in waypoints_spherical_deg][0:4]
N = len(waypoints_spherical)
p = rad.r_i(waypoints_spherical)
r = [rad.radius(p[(i-1):(i+2)]) for i in range(1, N-1)]
v = [start_vel] + [min([math.sqrt(r[i]*g_tol),340]) for i in range(1,N-2)]+[start_vel]
print v
t = rad.t_i(v, p)


fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
  
polynomial = xyz_quintic(waypoints_spherical, g_tol, start_vel,6)  
x_poly = polynomial#[0]
#y_poly = polynomial[1]
#z_poly = polynomial[2]

t_plot = np.linspace(t[0]+.1, t[-1], 500)


x = eval_polynomial(t_plot, x_poly, t)
#y = eval_polynomial(t_plot, y_poly, t)
#z = eval_polynomial(t_plot, z_poly, t)

p = rad.r_i(waypoints_spherical)
x_i = [point[0] for point in p]
#y_i = [point[1] for point in p]
#z_i = [point[2] for point in p]
#ax.scatter(x_i, y_i, z_i, c='r', marker='o')
plt.plot(t_plot, x, t, x_i)#, y, z,c='b',marker='+')


    
#ax.set_xlabel(r'$x(t)$')
#ax.set_ylabel(r'$y(t)$')
#ax.set_zlabel(r'$z(t)$')   
plt.title('Quintic Interpolation (LA-SF)')
plt.grid(True)
print("Task completed in  %s seconds" % (time.time() - start_time))

plt.show()


