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
        return lambda x: np.prod([(x-X[j])/(X[i]-X[j]) for j in range(D) if i != j]) * Y[i]
    Sx = [L(i) for i in range(D)]  # summands
    return lambda x: np.sum([s(x) for s in Sx])

def join_lists(*lists):
    return sum(lists, [])

# points is an array of points (ex: [[-1, 4], [0, 2], [1,6]])
# Returns N-d polynomials
def lagrange_polynomials(points, D):
    X = [pair[0] for pair in points]
    Y = [pair[1] for pair in points]
    polynomials = []
    for i in range(0, len(X) - D - 1):
        polynomials.append(lagrange_polynomial(X[i:i+(D+2)], Y[i:(D+2)], D))
    return polynomials

# coordinates is a list of N longitude and latitude points
# Returns r_i an array of tuples of (x_i, y_i, z_i)
def r_i(coordinates):
    r_i_results = []
    for coordinate in coordinates:
        x_i = R*math.cos(coordinate[0])*math.cos(coordinate[1])
        y_i = R*math.cos(coordinate[0])*math.sin(coordinate[1])
        z_i = R*math.sin(coordinate[0])
        r_i_results.append((x_i, y_i, z_i))
    return r_i_results

# v_i is a list of N-1 numbers
# returns a list of N numbers t_i
def t_i(v_i, r_i):
    t_i_results = [0]
    for i in range(0, len(v_i)):
        t_i = 0
        for k in range(0, i + 1):
            t_i += np.linalg.norm(np.subtract(r_i[k+1], r_i[k])) / v_i[i]
        t_i_results.append(t_i)

    return t_i_results

def F_i(t_i, r_i, D):
    N = len(t_i)
    t_i = np.array(t_i)
    r_i = np.array(r_i)
    np.column_stack((t_i,r_i[:,0]))
    f_i = lagrange_polynomials(np.column_stack((t_i,r_i[:,0])), D)
    g_i = lagrange_polynomials(np.column_stack((t_i,r_i[:,1])), D)
    h_i = lagrange_polynomials(np.column_stack((t_i,r_i[:,2])), D)
    return [[f_i[i], g_i[i], h_i[i]] for i in range(N-D-1)]   

def comfort_calculation(coordinates, v_i, D):
    r_i_results = r_i(coordinates)
    t_i_results = t_i(v_i, r_i_results)
    F_i_results = F_i(t_i_results, r_i_results, D)
    return F_i_results
#_________________________________END OF TASK 1a,b______________________________


#STUFF NEEDED TO PLOT THE RESULTS of TASK 1a,b
def plot_polynomials(points, polynomials, D):
    N = len(points)
    a = math.floor((D+1)/2)
    t_i = [point[0] for point in points]
    t_polys = [0]+[t_i[a+i] for i in range(N-D-2)]+[t_i[-1]]  #x-values at which the polynomial switches
    t_ranges = [np.linspace(t_polys[i], t_polys[i+1], 100) for i in range(N-D-1)]

    x = [map(polynomials[i][0],t_ranges[i]) for i in range(N-D-1)]
    y = [map(polynomials[i][1],t_ranges[i]) for i in range(N-D-1)]
    z = [map(polynomials[i][2],t_ranges[i]) for i in range(N-D-1)]
    x = join_lists(x)
    y = join_lists(y)
    z = join_lists(z)
    plt.plot(x, y, z,'ro')
    
    x_i = [point[1] for point in points]
    y_i = [point[2] for point in points]
    z_i = [point[3] for point in points]
    plt.plot(x_i, y_i, z_i,'ro')
    
    plt.xlabel(r'$f(t)$')
    plt.ylabel(r'$g(t)$')      
    plt.zlabel(r'$h(t)$')
    plt.title('Polynomial')
    plt.grid(True)
    plt.show()


#All that is needed for the job of interpolating 3D points:
coordinates = [[-0, 0], [math.pi/4, 0], [math.pi/4,math.pi/4],[math.pi/4,math.pi/2],[math.pi/4,math.pi/4]]
v_i_numbers = [2000,5000,10000,5000]
comfort_results = comfort_calculation(coordinates, v_i_numbers, 3)

#Extra work required to plot output:
points_xyz = r_i(coordinates)
points_t = t_i(v_i_numbers, points_xyz)
points_txyz = [[points_t[i],points_xyz[i][0],points_xyz[i][1],points_xyz[i][2]] for i in range(len(points_t))]
plot_polynomials(points_txyz, comfort_results[0], 3)
