"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import scipy.interpolate
import numpy as np

# Custom Modules:
import curvature


def smoothing_splines_2d(x_array, y_array, s_values, weights, smoothing_factor):
    x_spline = scipy.interpolate.UnivariateSpline(s_values, x_array, w=weights)
    x_spline.set_smoothing_factor(smoothing_factor)
    y_spline = scipy.interpolate.UnivariateSpline(s_values, y_array, w=weights)
    y_spline.set_smoothing_factor(smoothing_factor)
    return [x_spline, y_spline]

def set_smoothing_factors_2d(x_spline, y_spline, smoothing_factor):
    x_spline.set_smoothing_factor(smoothing_factor)
    y_spline.set_smoothing_factor(smoothing_factor)
    return [x_spline, y_spline]

def iterative_smoothing_interpolation_2d(x_array, y_array, initial_weights,
                                initial_smoothing_factor, curvature_threshold):
    num_points = x_array.size
    s_values = np.arange(num_points)
    x_spline, y_spline = smoothing_splines_2d(x_array, y_array, s_values,
                               initial_weights, initial_smoothing_factor)
    is_curvature_valid = curvature.curvature_test_2d(x_spline, y_spline,
                                          s_values, curvature_threshold)
    smoothing_multiple = 2.0
    max_smoothing_factor = 10**10
    min_smoothing_factor = 10**(-10)
    is_smoothing_factor_bounded_above = True
    is_smoothing_factor_bounded_below = True
    test_smoothing_factor = initial_smoothing_factor
    if is_curvature_valid:
        while is_curvature_valid and is_smoothing_factor_bounded_below:
            print test_smoothing_factor
            test_smoothing_factor *= 1.0/ smoothing_multiple
            set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
            is_curvature_valid = curvature.curvature_test_2d(x_spline, y_spline,
                                                  s_values, curvature_threshold)
            is_smoothing_factor_bounded_below = (test_smoothing_factor >
                                                  min_smoothing_factor)
        test_smoothing_factor *= smoothing_multiple
        set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
    else:
        while (not is_curvature_valid) and is_smoothing_factor_bounded_above:
            test_smoothing_factor *= smoothing_multiple
            set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
            is_curvature_valid = curvature.curvature_test_2d(x_spline, y_spline,
                                                  s_values, curvature_threshold)
            is_smoothing_factor_bounded_above = (test_smoothing_factor <
                                                  max_smoothing_factor)
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
            test_smoothing_factor *= 1.0 / smoothing_multiple
            set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
            is_error_valid = error_test_2d(x_spline, y_spline, s_values,
                                            max_error, x_array, y_array)
        test_smoothing_factor *= smoothing_multiple
        set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
    else:
        while is_error_valid:
            test_smoothing_factor *= smoothing_multiple
            set_smoothing_factors_2d(x_spline, y_spline, test_smoothing_factor)
            is_error_valid = error_test_2d(x_spline, y_spline, s_values,
                                           max_error, x_array, y_array)
    return [x_spline, y_spline]

def bounded_error_graph_interpolation(graph_points, resolution):
    points_array = np.array([np.array(point) for point in graph_points])
    s_vals = np.arange(len(graph_points))
    points_x_vals_array, points_y_vals_array = np.transpose(points_array)
    end_weights = 10**3
    weights = np.empty(len(graph_points))
    weights.fill(1)
    weights[0] = weights[-1] = end_weights
    smoothing_factor = 10**4
    x_spline, y_spline = smoothing_interpolation_with_max_error(
        points_x_vals_array, points_y_vals_array, s_vals, weights,
                                     smoothing_factor, resolution)
    sampled_x_vals = x_spline(s_vals)
    sampled_y_vals = y_spline(s_vals)
    interpolated_points = np.transpose([sampled_x_vals, sampled_y_vals])
    curvature_array_2d = curvature.parametric_splines_2d_curvature(x_spline,
                                                           y_spline, s_vals)
    return [interpolated_points, curvature_array_2d]

def get_bounded_curvature_graph_interpolation(graph_points, max_curvature):
    x_vals, y_vals = np.transpose(graph_points)
    num_points = graph_points.shape[0]
    s_vals = np.arange(num_points)
    end_weights = 10**3
    weights = np.empty(num_points)
    weights.fill(1)
    weights[0] = weights[-1] = end_weights
    smoothing_factor = 10**4
    x_spline, y_spline = iterative_smoothing_interpolation_2d(x_vals, y_vals,
                                    weights, smoothing_factor, max_curvature)
    curvature_array_2d = curvature.parametric_splines_2d_curvature(x_spline,
                                                           y_spline, s_vals)
    x_vals = x_spline(s_vals)
    y_vals = y_spline(s_vals)
    return [[x_vals, y_vals], curvature_array_2d]

def bounded_curvature_extrema_interpolate(x_vals, y_vals, extrema_indices,
                                                            max_curvature):
    extrema_weight = 10**3
    smoothing_factor = 10**4
    num_points = len(x_vals)
    s_vals = np.arange(num_points)
    weights = np.empty(num_points)
    weights.fill(1)
    for i in extrema_indices:
        weights[i] = extrema_weight    
    x_spline, y_spline = iterative_smoothing_interpolation_2d(x_vals, y_vals,
                                    weights, smoothing_factor, max_curvature)
    curvature_array_2d = curvature.parametric_splines_2d_curvature(x_spline,
                                                           y_spline, s_vals)
    y_vals = y_spline(s_vals)
    return [y_vals, curvature_array_2d]

                                                      
