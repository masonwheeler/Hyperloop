#!/usr/bin/env python
import math
import numpy as np
from matplotlib import pyplot as plt

R =  6.371*(10**6)


# Calculate the unique lagrange polynomial of degree D that goes trough points X and Y
# Returns the unique lagrange polynomial of degree D
def lagrange_polynomial(X, Y, D):
    def L(i):
        return lambda x: np.prod([(x-X[j])/(X[i]-X[j]) for j in range(len(X)) if i != j]) * Y[i]
    Sx = [L(i) for i in range(0, D + 1)]  # summands
    return lambda x: np.sum([s(x) for s in Sx])


# points is an array of points (ex: [[-1, 4], [0, 2], [1,6]])
# Returns N-d polynomials
def lagrange_polynomials(points, d):
    X = points[:,0]
    Y = points[:,1]
    polynomials = []
    for i in range(0, len(X) - d):
        polynomials.append(lagrange_polynomial(X[i:i+(d+2)], Y[i:(d+2)], d))
    return polynomials

def plot_polynomial(points, polynomial):
    X = [pair[0] for pair in points]
    Y = [pair[1] for pair in points]
    x_range = np.linspace(X[0], X[-1], 100)
    print x_range
    plt.plot(X, Y, 'ro')
    plt.plot(x_range, map(polynomial, x_range))
    plt.xlabel(r'$x$')
    plt.ylabel(r'$F(x)$')
    plt.title('Polynomial')
    plt.grid(True)
    plt.show()


#
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
    t_i = np.array(t_i)
    r_i = np.array(r_i)
    np.column_stack((t_i,r_i[:,0]))
    f_i = lagrange_polynomials(np.column_stack((t_i,r_i[:,0])), D)
    g_i = lagrange_polynomials(np.column_stack((t_i,r_i[:,1])), D)
    h_i = lagrange_polynomials(np.column_stack((t_i,r_i[:,2])), D)
    return [f_i, g_i, h_i]

def comfort_calculation(coordinates, v_i, D):
    r_i_results = r_i(coordinates)
    t_i_results = t_i(v_i, r_i_results)

    F_i_results = F_i(t_i_results, r_i_results, D)
    return F_i_results

coordinates = [[-1, 4], [0, 2], [1,6]]
v_i_numbers = [2,5]


comfort_results = comfort_calculation(coordinates, v_i_numbers, 2)
comfort_results = np.array(comfort_results)
X = [pair[0] for pair in coordinates]
Y = [pair[1] for pair in coordinates]
print "This is {x_i}:" 
print X
print "This is {F(x_i)}:"
print Y
polynomial = lagrange_polynomial(X,Y,2)
print polynomial(0)
plot_polynomial(coordinates, polynomial)
