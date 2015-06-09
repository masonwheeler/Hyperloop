import math
import numpy as np
import time
import scipy
import scipy.interpolate
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import radiusOfCurvature as rad
import quintic as quint
import feedBCs as bc

def Points_to_Coeffs(tht_i_phi_i, n):
	t, p, v = bc.parse(tht_i_phi_i)
	Gx = bc.process(t, p, v, n, 0)
	Gy = bc.process(t, p, v, n, 1)
	Gz = bc.process(t, p, v, n, 2)
	ax = []
	ay = []
	az = []
	for i in range(len(Gx)):
		ax += quint.interp(Gx[i])
		ay += quint.interp(Gy[i])
		az += quint.interp(Gz[i])
	return [ax, ay, az, t]

def Coeffs_to_Vals(a, s, t_i):
	condlist = [(t_i[j] < s)*(s < t_i[j+1]) for j in range(len(t_i)-2)]
	def f(k):
		return lambda x: sum([a[k][j] * (x)**j for j in range(len(a[k]))])
	funclist = [f(k) for k in range(len(a))]
	return np.piecewise(s, condlist, funclist)


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
# fig = plt.figure()
# subplot = fig.add_subplot(111, projection='3d')
  
# ax, ay, az, t = Points_to_Coeffs(tht_i_phi_i, 6)
# s = np.linspace(t[0]+.05,t[-1]-.05, 500)
# x_plot = Coeffs_to_Vals(ax, s, t)
# y_plot = Coeffs_to_Vals(ay, s, t)
# z_plot = Coeffs_to_Vals(az, s, t)
# subplot.scatter(x_plot, y_plot, z_plot, c='b', marker='+')



# p = rad.r_i(tht_i_phi_i)
# x_i = [point[0] for point in p]
# y_i = [point[1] for point in p]
# z_i = [point[2] for point in p]
# subplot.scatter(x_i, y_i, z_i, c='r', marker='o')


    
# subplot.set_xlabel(r'$x(t)$')
# subplot.set_ylabel(r'$y(t)$')
# subplot.set_zlabel(r'$z(t)$')   
# plt.title('Quintic Interpolation (LA-SF)')
# plt.grid(True)
# print("Task completed in  %s seconds" % (time.time() - start_time))

# plt.show()


