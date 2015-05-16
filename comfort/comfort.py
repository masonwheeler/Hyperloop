#!/usr/bin/env python
import math
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

R =  6.371*(10**6)

#TASK 1a-b:

# Calculate the unique lagrange polynomial of degree D that goes trough points X and Y
# Returns the unique lagrange polynomial of degree D
def lagrange_polynomial(X, Y, D):
    def L(i):
        return lambda x: np.prod([(x-X[j])/(X[i]-X[j]) for j in range(D+1) if i != j]) * Y[i]
    Sx = [L(i) for i in range(D+1)]  # summands
    return lambda x: np.sum([s(x) for s in Sx])

def join_lists(lists):
   return reduce(lambda x, y: x + y, lists)

# points is an array of points (ex: [[-1, 4], [0, 2], [1,6]])
# Returns N-d polynomials
def lagrange_polynomials(points, D):
    X = [pair[0] for pair in points]
    Y = [pair[1] for pair in points]
    polynomials = []
    for i in range(len(X) - D):
        polynomials.append(lagrange_polynomial(X[i:i+(D+1)], Y[i:i+(D+1)], D))
    return polynomials

# coordinates is a list of N longitude and latitude points
# Returns r_i an array of tuples of (x_i, y_i, z_i)
def r_i(coordinates):
    r_i_results = []
    for coordinate in coordinates:
        x_i = R*math.cos(coordinate[0])*math.cos(coordinate[1])
        y_i = R*math.cos(coordinate[0])*math.sin(coordinate[1])
        z_i = R*math.sin(coordinate[0])
        r_i_results.append([x_i, y_i, z_i])
    return r_i_results

# v_i is a list of N-1 numbers
# returns a list of N numbers t_i
def t_i(v_i, r_i):  #you made a mistake here.
    t_i_results = [0]
    for i in range(len(v_i)):
        t_i = t_i_results[i] + np.linalg.norm(np.subtract(r_i[i+1], r_i[i])) / v_i[i]
        t_i_results.append(t_i)
    return t_i_results

def F_i(t_i, r_i, D):
    N = len(t_i)
    f_i = lagrange_polynomials([[t_i[i],r_i[i][0]] for i in range(N)], D)
    g_i = lagrange_polynomials([[t_i[i],r_i[i][1]] for i in range(N)], D)
    h_i = lagrange_polynomials([[t_i[i],r_i[i][2]] for i in range(N)], D)
    return [[f_i[i], g_i[i], h_i[i]] for i in range(N-D)]   

def comfort_calculation(coordinates, v_i, D):
    r_i_results = r_i(coordinates)
    t_i_results = t_i(v_i, r_i_results)
    F_i_results = F_i(t_i_results, r_i_results, D)
    return F_i_results
#_________________________________END OF TASK 1a,b______________________________


#STUFF NEEDED TO PLOT THE RESULTS of TASK 1a,b
def plot_polynomials(points, polynomials, D):
    N = len(points)
    a = int(math.floor((D-1)/2))
    t_i = [point[0] for point in points]
    t_polys = [0]+[t_i[a+i] for i in range(N-D-1)]+[t_i[-1]]  #x-values at which the polynomial switches
    t_ranges = [np.linspace(t_polys[i], t_polys[i+1], 100) for i in range(N-D)]

    x = [map(polynomials[i][0],t_ranges[i]) for i in range(N-D)]
    y = [map(polynomials[i][1],t_ranges[i]) for i in range(N-D)]
    z = [map(polynomials[i][2],t_ranges[i]) for i in range(N-D)]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    x = join_lists(x)
    y = join_lists(y)
    z = join_lists(z)

    ax.scatter(x, y, z,c='b',marker='+')

    x_i = [point[1] for point in points]
    y_i = [point[2] for point in points]
    z_i = [point[3] for point in points]
    ax.scatter(x_i, y_i, z_i, c='r', marker='o')
    
    ax.set_xlabel(r'$f(t)$')
    ax.set_ylabel(r'$g(t)$')
    ax.set_zlabel(r'$h(t)$')   
    plt.title('Interpolation (LA-SF)')
    plt.grid(True)
    plt.show()



#All that is needed for the job of interpolating 3D points:
coordinates = [
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
coordinates=[[2*math.pi*point[0]/360,2*math.pi*point[1]/360] for point in coordinates]
v_i_numbers = [100*i for i in range(1,len(coordinates))]
comfort_results = comfort_calculation(coordinates, v_i_numbers, 3)

#Extra work required to plot output:
points_xyz = r_i(coordinates)
points_t = t_i(v_i_numbers, points_xyz)
points_txyz = [[points_t[i],points_xyz[i][0],points_xyz[i][1],points_xyz[i][2]] for i in range(len(points_t))]
plot_polynomials(points_txyz, comfort_results, 3)
