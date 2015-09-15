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

# Standard Modules:
import math
import numpy as np
import random
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

# Custom Modules:
import util
import curvature

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


def quint(t, x, dx_0, dx_n):
    """ For an exposition of the quintic interpolation method see Polyakov (79.)
    """
    N = len(x) - 1  # number of viapoints
    d2x_0 = d2x_n = 0
    b_0 = np.array([x[0], dx_0, d2x_0])  # initial position and derivatives
    b_n = np.array([x[N], dx_n, d2x_n])  # final position and derivatives

    def b_j(j):
        return np.array([x[j], 0, 0, 0, 0, x[j]])

    C = np.zeros((6 * N, 6 * N))
    b = np.zeros(6 * N)

    b[0:3] = b_0
    b[6 * N - 3:6 * N] = b_n
    for j in range(1, N):
        b[3 + 6 * (j - 1):3 + 6 * j] = b_j(j)

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

#Customizations of quintic interpolation

def join_indices(N):
    if N <= 5:
        return []
    else:
        m, k = divmod(N, 5)
        if k >= 2:
            return [5 * j for j in range(1, m + 1)]
        else:
            return [5 * j for j in range(1, m)] + [int(5 * (m - 1) + np.ceil((5 + k) /  2.))]

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
        polys = quint(t[:J[0] + 1], x[:J[0] + 1], 0, u[0]) + sum([quint(t[J[i]:J[i +    1] + 1], x[J[i]:J[i + 1] + 1],
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

#Refactored Version

def get_boundary_indices(num_intervals):
    if num_intervals <= 5:
        boundary_indices = []
    else:
        num_indices_partitions, num_leftover_indices  = divmod(num_intervals, 5)
        if num_leftover_indices >= 2:
            boundary_indices = [5 * (j + 1) for j
                                in range(num_indices_partitions)]
        else:
            boundary_indices = [5 * (j + 1) for j
                                in range(num_indices_partitions - 1)]
            last_offset = np.ceil((5 + num_leftover_indices) / 2.0)
            last_index = int(5 * (m - 1) + last_offset)
            boundary_indices.append(last_index)
    return boundary_indices

def build_extended_quintic(s, x):
    """
    Extends quint() to allow for high numbers (> 5) of waypoints to be
    interpolated, without running into ill-conditioning problems.
    """
    num_intervals = len(s) - 1
    boundary_indices = get_boundary_indices(num_intervals)
    if len(boundary_indices) == 0:
        first_derivative_initial_value = 0
        first_derivative_final_value = 0
        partitions_quintic_coeffs = quint(s, x, first_derivative_initial_value,
                                                  first_derivative_final_value)
    else:
        boundary_first_derivatives = []
        initial_first_derivative = 0
        boundary_first_derivatives.append(initial_first_derivative)
        for i in boundary_indices: 
             boundary_first_derivative = ((x[i + 1] - x[i - 1]) /
                                          (s[i + 1] - s[i - 1]))
             boundary_first_derivatives.append(boundary_first_derivative)
        final_first_derivative = 0
        boundary_first_derivatives.append(final_first_derivative)

        boundary_indices_pairs = util.to_pairs(boundary_indices)

        s_partitions = []
        for boundary_index_pair in boundary_indices_pairs:
            boundary_index_a, boundary_index_b = boundary_index_pair
            s_partition = s[joined_index_a : joined_index_b + 1]
            s_partitions.append(s_partition)
        
        x_partitions = []
        for boundary_index_pair in boundary_indices_pairs:
            boundary_index_a, boundary_index_b = boundary_index_pair
            x_partition = x[joined_index_a : joined_index_b + 1]
            x_partitions.append(x_partition)

        partitions_quintic_coeffs = []
        for i in range(len(joined_indices) - 1):
            partition_quintic_coeff = quint(s_partitions[i],
                                            x_partitions[i],
                              boundary_first_derivatives[i],
                          boundary_first_derivatives[i + 1])
            partitions_quintic_coeffs.append(partition_quintic_coeff)   
    return partitions_quintic_coeffs

def sample_s_vals(s_vals, num_samples_per_partition):
    num_intervals = len(s_vals) - 1
    partitions_sampled_s_vals = []
    for i in range(num_intervals):
        partition_sampled_s_vals = []
        for each_int in range(num_samples_per_partition):
            fraction_along = float(each_int) / float(num_samples_per_partition)
            sampled_s_val = s_vals[i] + fraction_along * (s_vals[i+1] - s_vals[i])
            partition_sampled_s_vals.append(sampled_s_val)
        partitions_sampled_s_vals.append(partition_sampled_s_vals)
    return partitions_sampled_s_vals

def get_standard_powers(s_val):
    s_powers = [1, s_val, s_val**2, s_val**3, s_val**4, s_val**5]
    return s_powers

def get_first_derivative_powers(s_val):
    s_powers = [1, 2*s_val, 3*s_val**2, 4*s_val**3, 5*s_val**4, 0]
    return s_powers

def get_second_derivative_powers(s_val):
    s_powers = [2, 6*s_val, 12*s_val**2, 20*s_val**3, 0, 0]
    return s_powers

def evaluate_coeffs(partitions_sampled_s_vals, partitions_quintic_coeffs,
                    powers_function):
    partitions_sampled_s_vals_quintic_coeffs_pairs = zip(
        partitions_sampled_s_vals, partitions_quintic_coeffs)
    sampled_vals = []    
    for partition_sampled_s_vals_quintic_coeffs_pair \
     in partitions_sampled_s_vals_quintic_coeffs_pairs:
        partition_sampled_s_vals, partition_quintic_coeffs = \
            partition_sampled_s_vals_quintic_coeffs_pair
        for s_val in partition_sampled_s_vals:
            s_powers = powers_function(s_val)
            sampled_val = np.dot(partition_quintic_coeffs, s_powers)
            sampled_vals.append(sampled_val)
    sampled_vals_array = np.array(sampled_vals)
    return sampled_vals_array

def evaluate_coeffs_standard(partitions_sampled_s_vals,
                             partitions_quintic_coeffs):
    sampled_x_vals = evaluate_coeffs(partitions_sampled_s_vals,
                                     partitions_quintic_coeffs,
                                     get_standard_powers)
    return sampled_x_vals

def evaluate_coeffs_first_derivatives(partitions_sampled_s_vals,
                             partitions_quintic_coeffs):
    sampled_first_derivatives = evaluate_coeffs(partitions_sampled_s_vals,
                                                partitions_quintic_coeffs,
                                                get_first_derivative_powers)
    return sampled_first_derivatives

def evaluate_coeffs_second_derivatives(partitions_sampled_s_vals,
                             partitions_quintic_coeffs):
    sampled_second_derivatives = evaluate_coeffs(partitions_sampled_s_vals,
                                                partitions_quintic_coeffs,
                                                get_second_derivative_powers)
    return sampled_second_derivatives

def compute_quintic_curvature(partitions_sampled_s_vals, x_quintic_coeffs,
                                                         y_quintic_coeffs):
    x_first_deriv_values = evaluate_coeffs_first_derivatives(
                 partitions_sampled_s_vals, x_quintic_coeffs)
    x_second_deriv_values = evaluate_coeffs_second_derivatives(
                   partitions_sampled_s_vals, x_quintic_coeffs)
    y_first_deriv_values = evaluate_coeffs_first_derivatives(
                 partitions_sampled_s_vals, y_quintic_coeffs)
    y_second_deriv_values = evaluate_coeffs_second_derivatives(
                   partitions_sampled_s_vals, y_quintic_coeffs)
    quintic_curvature_array = curvature.compute_curvature_array_2d(
                                              x_first_deriv_values,
                                             x_second_deriv_values,
                                              y_first_deriv_values,
                                             y_second_deriv_values)
    return quintic_curvature_array

def parametric_extended_quintic(points, num_samples_per_partition=25,
                                             num_s_vals_per_x_val=15):
    """
    Parametric version of extended_quintic.
    """
    s_vals = [num_s_vals_per_x_val * n for n in range(len(points))]
    points_x_vals, points_y_vals = np.transpose(points)
    x_quintic_coeffs = build_extended_quintic(s_vals, points_x_vals)
    y_quintic_coeffs = build_extended_quintic(s_vals, points_y_vals)
    partitions_sampled_s_vals = sample_s_vals(s_vals, num_samples_per_partition)
    sampled_x_vals = evaluate_coeffs_standard(partitions_sampled_s_vals,
                                              x_quintic_coeffs)
    sampled_y_vals = evaluate_coeffs_standard(partitions_sampled_s_vals,
                                              y_quintic_coeffs)
    interpolated_points = np.transpose([sampled_x_vals, sampled_y_vals])
    quintic_curvature_array = compute_quintic_curvature(
                                  partitions_sampled_s_vals,
                                           x_quintic_coeffs,
                                           y_quintic_coeffs)
    return [interpolated_points, quintic_curvature_array]

"""
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
"""

# Test quint(t, x, v1, v2):
"""
t = [i for i in range(6)]
x = [random.uniform(-10,10) for i in range(len(t))]
v1 = random.uniform(-10,10)
v2 = random.uniform(-10,10)
print "x is:"
print x
print "t is:"
print t
print "(v1, v2) is:"
print [v1, v2]

polys = quint(t, x, v1, v2)

t_m = [[t[i]+(m/100.)*(t[i+1]-t[i]) for m in range(100)] for i in range(len(t)-1)]
x_m = [[np.dot(polys[i],[1,time,time**2,time**3,time**4,time**5]) for time in t_m[i]] for i in range(len(t_m))]
t_m = sum(t_m, [])
x_m = sum(x_m, [])

print "x_m is:"
print x_m
print "t_m is:"
print t_m
plt.plot(t_m, x_m, t, x)
plt.show()
"""

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
