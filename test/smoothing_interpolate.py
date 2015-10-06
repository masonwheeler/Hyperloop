"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import scipy.interpolate
import numpy as np

# Custom Modules:
import curvature

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
    is_error_valid = (largest_error <= max_error)
    return is_error_valid

def smoothing_interpolation_with_max_error(x_array, y_array, s_values,
             initial_end_weights, initial_smoothing_factor, max_error):
    x_spline, y_spline = smoothing_splines_2d(x_array, y_array, s_values,
                                  initial_end_weights, initial_smoothing_factor)
    is_error_valid = error_test_2d(x_spline, y_spline, s_values, max_error,
                                   x_array, y_array)
    smoothing_multiple = 2.0
    test_smoothing_factor = initial_smoothing_factor
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
    return [x_spline, y_spline]

def bounded_error_graph_interpolation(graph_points, resolution):
    points_array = np.array([np.array(point) for point in graph_points])
    s_vals = np.arange(len(graph_points))
    points_x_vals_array, points_y_vals_array = np.transpose(points_array)
    initial_end_weights = 10**3
    initial_smoothing_factor = 10**4
    x_spline, y_spline = \
        smoothing_interpolate.smoothing_interpolation_with_max_error(
                                                   points_x_vals_array,
                                                   points_y_vals_array,
                                                                s_vals,
                                                   initial_end_weights,
                                              initial_smoothing_factor,
                                                            resolution)
    sampled_x_vals = x_spline(s_vals)
    sampled_y_vals = y_spline(s_vals)
    interpolated_points = np.transpose([sampled_x_vals, sampled_y_vals])
    curvature_array_2d = curvature.parametric_splines_2d_curvature(x_spline,
                                                                   y_spline,
                                                                     s_vals)
    return [interpolated_points, curvature_array_2d]


