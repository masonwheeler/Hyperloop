"""
Original Developer: Jonathan Ward
Purpose of Module: To provide interpolation functions.
Last Modified: 8/13/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added function to set smoothing factor
"""

# Standard Modules:
import scipy.interpolate
import numpy as np

# Our Modules:
import util
import config
import curvature
import parameters

########## For Edge Sampling ##########

def points_to_edges(points):
    return util.to_pairs(points)

def distance_along_edge_to_point(edge, distance_along_edge):
    edge_start, edge_end = edge
    edge_vector = util.subtract(edge_end, edge_start)
    edge_length = util.norm(edge_vector)
    scale_factor = distance_along_edge / edge_length
    scaled_vector = util.scale(scale_factor, edge_vector)
    point = util.add(scaled_vector, edge_start)
    return point

def sample_edge(edge, sample_spacing, distance_along_edge, start_arc_length):
    edge_length = util.norm(util.edge_to_vector(edge))
    edge_points = []
    edge_arc_lengths = []
    while distance_along_edge <= edge_length:
        point = distance_along_edge_to_point(edge, distance_along_edge)
        edge_points.append(point)
        distance_along_edge += sample_spacing
        point_arc_length = distance_along_edge + start_arc_length
        edge_arc_lengths.append(point_arc_length)
    distance_along_edge -= edge_length
    return [edge_points, edge_arc_lengths, distance_along_edge]

def sample_edges(edges, sample_spacing):
    distance_along_edge = 0
    start_arc_length = 0
    points = []
    arc_lengths = []    
    for edge in edges:
        edge_points, edge_arc_lengths, distance_along_edge = \
        sample_edge(edge, sample_spacing, distance_along_edge, start_arc_length)
        start_arc_length = edge_arc_lengths[-1]
        points += edge_points
        arc_lengths += edge_arc_lengths
    return [points, arc_lengths]

def sample_path(path_points, path_sample_spacing):
    path_edges = points_to_edges(path_points)
    sampled_path_points, sampled_arc_lengths = sample_edges(path_edges,
                                                            path_sample_spacing)
    path_vectors = [util.edge_to_vector(edge) for edge in path_edges]
    edge_lengths = [util.norm(vector) for vector in path_vectors]
    last_arc_length = sum(edge_lengths)   
    last_point = path_points[-1]
    sampled_arc_lengths.append(last_arc_length)
    sampled_path_points.append(last_point)
    return [sampled_path_points, sampled_arc_lengths]

########## Auxilary Functions ##########


def points_2d_to_arrays(points2d):
    x_coords_list, y_coords_list = zip(*points2d)
    x_array, y_array = np.array(x_coords_list), np.array(y_coords_list)
    return [x_array, y_array]


def points_3d_to_arrays(points3d):
    x_coords_list, y_coords_list, z_coords_list = zip(*points3d)
    x_array = np.array(x_coords_list)
    y_array = np.array(y_coords_list)
    z_array = np.array(z_coords_list)
    return [x_array, y_array, z_array]


def get_s_values(num_points):
    s_values = np.arange(0.0, float(num_points))
    return s_values


def get_spline_values(spline, s_values):
    spline_values = spline(s_values)
    return spline_values


def get_slice_s_values(s_values, nth):
    last_s_value = s_values[-1]
    slice_s_values = s_values[::nth]
    slice_s_values = np.append(slice_s_values, last_s_value)
    return slice_s_values

########## For 2d Smoothing Splines ##########


def smoothing_splines_2d(x_array, y_array, s_values, end_weights, smoothing_factor):
    num_points = s_values.size
    weights = np.ones(num_points)
    weights[0] = weights[-1] = end_weights

    x_spline = scipy.interpolate.UnivariateSpline(s_values, x_array, weights)
    x_spline.set_smoothing_factor(smoothing_factor)
    y_spline = scipy.interpolate.UnivariateSpline(s_values, y_array, weights)
    y_spline.set_smoothing_factor(smoothing_factor)
    return [x_spline, y_spline]


def set_smoothing_factors_2d(x_spline, y_spline, smoothing_factor):
    x_spline.set_smoothing_factor(smoothing_factor)
    y_spline.set_smoothing_factor(smoothing_factor)
    return [x_spline, y_spline]

def iterative_smoothing_interpolation_2d(x_array, y_array, initial_end_weights,
                                initial_smoothing_factor, curvature_threshold):
    num_points = x_array.size
    s_values = np.arange(num_points)
    x_spline, y_spline = smoothing_splines_2d(x_array, y_array, s_values,
                                  initial_end_weights, initial_smoothing_factor)
    is_curvature_valid = curvature.curvature_test_2d(x_spline, y_spline,
                                          s_values, curvature_threshold)
    smoothing_multiple = 2.0
    test_smoothing_factor = initial_smoothing_factor
    if is_curvature_valid:
        while is_curvature_valid:
            test_smoothing_factor *= 1.0/ smoothing_multiple
            set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
            is_curvature_valid = curvature.curvature_test_2d(x_spline, y_spline,
                                                  s_values, curvature_threshold)
        test_smoothing_factor *= smoothing_multiple
        set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
        return [x_spline, y_spline]
    else:
        while not is_curvature_valid:
            test_smoothing_factor *= smoothing_multiple
            set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
            is_curvature_valid = curvature.curvature_test_2d(x_spline, y_spline,
                                                  s_values, curvature_threshold)
            print(is_curvature_valid)
        return [x_spline, y_spline]

def error_test_2d(x_spline, y_spline, s_values, max_error, x_array, y_array):
    interpolated_x_array = x_spline(s_values)
    interpolated_y_array = y_spline(s_values)
    x_differences = interpolated_x_array - x_array
    y_differences = interpolated_y_array - y_array
    points_errors = np.hypot(x_differences, y_differences)
    largest_error = np.amax(points_errors)
    ##print("largest error: " + str(largest_error))
    is_error_valid = (largest_error <= max_error)   
    ##print("is error valid: " + str(is_error_valid))
    return is_error_valid

import time
def smoothing_interpolation_with_max_error(x_array, y_array, s_values,
             initial_end_weights, initial_smoothing_factor, max_error):
    x_spline, y_spline = smoothing_splines_2d(x_array, y_array, s_values,
                                  initial_end_weights, initial_smoothing_factor)
    is_error_valid = error_test_2d(x_spline, y_spline, s_values, max_error,
                                   x_array, y_array)
    smoothing_multiple = 2.0
    test_smoothing_factor = initial_smoothing_factor
    print "array size: " 
    print x_array.size
    if is_error_valid:
        while not is_error_valid:
            print(test_smoothing_factor)
            test_smoothing_factor *= 1.0 / smoothing_multiple
            set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
            is_error_valid = error_test_2d(x_spline, y_spline, s_values,
                                            max_error, x_array, y_array)
        test_smoothing_factor *= smoothing_multiple
        set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
    else:
        while is_error_valid:
            print(test_smoothing_factor)
            test_smoothing_factor *= smoothing_multiple
            set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
            is_error_valid = error_test_2d(x_spline, y_spline, s_values,
                                           max_error, x_array, y_array)
    #time.sleep(1)
    return [x_spline, y_spline]

########## For Interpolating Splines ##########


def interpolate_points_1d(points1d):
    num_points = len(points1d)
    s_values = get_s_values(num_points)
    z_array = np.array(points1d)
    z_spline = scipy.interpolate.InterpolatedUnivariateSpline(
        s_values, z_array)
    return [z_spline, s_values]


def interpolating_splines_2d(x_array, y_array, s_values):
    x_spline = scipy.interpolate.InterpolatedUnivariateSpline(
        s_values, x_array)
    y_spline = scipy.interpolate.InterpolatedUnivariateSpline(
        s_values, y_array)
    return [x_spline, y_spline]


def interpolate_points_2d(points2d):
    num_points = len(points2d)
    s_values = get_s_values(num_points)
    x_array, y_array = points_2d_to_arrays(points2d)
    x_spline, y_spline = interpolating_splines_2d(x_array, y_array, s_values)
    return [x_spline, y_spline, s_values]


def interpolating_splines_3d(x_array, y_array, z_array, s_values):
    x_spline = scipy.interpolate.InterpolatedUnivariateSpline(
        s_values, x_array)
    y_spline = scipy.interpolate.InterpolatedUnivariateSpline(
        s_values, y_array)
    z_spline = scipy.interpolate.InterpolatedUnivariateSpline(
        s_values, z_array)
    return [x_spline, y_spline, z_spline]


def interpolate_points_3d(points3d):
    num_points = len(points3d)
    s_values = get_s_values(num_points)
    x_array, y_array, z_array = points_3d_to_arrays(points3d)
    x_spline, y_spline, z_spline = interpolating_splines_3d(x_array, y_array,
                                                            z_array, s_values)
    return [x_spline, y_spline, z_spline, s_values]


def points_1d_local_max_allowed_vels(points1d):
    z_spline, s_values = interpolate_points_1d(points1d)
    local_max_allowed_vels1d = effective_max_allowed_vels_1d(
        z_spline, s_values)
    return local_max_allowed_vels1d

def points_3d_local_max_allowed_vels(points3d):
    x_spline, y_spline, z_spline, s_values = interpolate_points_3d(points3d)
    local_max_allowed_vels = effective_max_allowed_vels(x_spline, y_spline, z_spline,
                                                        s_values)
    return local_max_allowed_vels

#def compute_interpolation_errors_2d(path_points, resolution):
#    sampled_path_points = sample_path_points(path_points, resolution)
    

def curvature_metric(graph_curvature_array):
    curvature_size = graph_curvature_array.size
    curvature_threshhold = np.empty(curvature_size)
    curvature_threshold_value = curvature.compute_curvature_threshold(
                             parameters.MAX_SPEED, parameters.MAX_LATERAL_ACCEL)
    curvature_threshhold.fill(curvature_threshold_value)
    absolute_curvature = np.absolute(graph_curvature_array)
    relative_curvature = np.subtract(absolute_curvature, curvature_threshhold)
    excess_curvature = relative_curvature.clip(min=0)
    curvature_metric = np.sqrt(np.mean(np.square(excess_curvature)))
    return curvature_metric * 10**10


def graph_curvature(graph_points, graph_sample_spacing):
    graph_edges = points_to_edges(graph_points)
    sampled_graph_points = sample_edges(graph_edges, graph_sample_spacing)
    x_array, y_array = points_2d_to_arrays(sampled_graph_points)
    num_points = x_array.size
    s_values = get_s_values(num_points)
    x_spline, y_spline = interpolating_splines_2d(x_array, y_array, s_values)
    graph_curvature_array = curvature.parametric_splines_2d_curvature(x_spline,
                                                            y_spline, s_values)
    graph_curvature = curvature_metric(graph_curvature_array)
    return graph_curvature
