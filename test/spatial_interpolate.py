"""
Original Developer:
    Jonathan Ward
"""
import numpy as np
import interpolate
import curvature

def scipy_smoothing(points, resolution):
    points_array = np.array([np.array(point) for point in points])
    s_vals = np.arange(len(points))
    points_x_vals_array, points_y_vals_array = np.transpose(points)
    initial_end_weights = 10**3
    initial_smoothing_factor = 10**4
    x_spline, y_spline = interpolate.smoothing_interpolation_with_max_error(
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

