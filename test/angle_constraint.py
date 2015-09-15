"""
Original Developer: 
    Jonathan Ward
"""

import numpy as np

import math
import config
import curvature
import advanced_interpolate
import util
import visualize

def test_path_points(path_points):
    sampled_path_points = interpolate.sample_path(path_points, 500)
    #print("sampled points: " + str(sampled_path_points))
                                           #config.BASE_RESOLUTION)
    x_spline, y_spline, s_values = interpolate.interpolate_points_2d(
                                                            sampled_path_points)
    curvature_array_2d = curvature.parametric_splines_2d_curvature(
                                            x_spline, y_spline, s_values)
    curvature_threshold = curvature.compute_curvature_threshold(
                                            parameters.MAX_SPEED/2.0,
                                            parameters.MAX_LATERAL_ACCEL)
    is_curvature_acceptable = curvature.test_curvature_validity(
                        curvature_array_2d, curvature_threshold)
    return is_curvature_acceptable

def test_path_points_v2(path_points, interpolator, max_curvature):
    naive_curvature = curvature.compute_naive_curvature(path_points)
    is_curvature_acceptable = naive_curvature < max_curvature
    return is_curvature_acceptable

def test_path_points_v3(path_points, interpolator, max_curvature):
    interpolated_points, curvature_array = interpolator(path_points)
    print(max_curvature)
    print(curvature_array)
    is_curvature_acceptable = curvature.test_curvature_validity(
                                 curvature_array, max_curvature)     
    path_points_x_vals, path_points_y_vals = zip(*path_points)  
    plottable_path_points = [path_points_x_vals, path_points_y_vals]
    plottable_path = [plottable_path_points, 'r-']    
    visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_path)
    interpolated_x_vals, interpolated_y_vals = np.transpose(interpolated_points)
    plottable_interpolated_points = [interpolated_x_vals, interpolated_y_vals]
    plottable_interpolation = [plottable_interpolated_points, 'b-']
    visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_interpolation)
    visualize.plot_objects(visualize.PLOT_QUEUE_SPATIAL_2D, False)
    visualize.PLOT_QUEUE_SPATIAL_2D.pop()
    visualize.PLOT_QUEUE_SPATIAL_2D.pop()
    return is_curvature_acceptable

def compute_degree_constraint(length_scale, max_curvature):
    interpolator = advanced_interpolate.parametric_extended_quintic
    origin = [0, 0]
    point_a = [length_scale, 0]
    angle_constraint_in_degrees = 0
    effective_angle_in_degrees = 180 - angle_constraint_in_degrees
    effective_angle_in_radians = math.radians(effective_angle_in_degrees)
    raw_point_b = [math.cos(effective_angle_in_radians) * length_scale,
                   math.sin(effective_angle_in_radians) * length_scale]
    point_b = util.round_nums(raw_point_b)
    path_points = [point_a, origin, point_b]
    while True:
        is_curvature_acceptable = test_path_points_v3(path_points, interpolator,
                                                                  max_curvature)
        if is_curvature_acceptable:                        
            angle_constraint_in_degrees += 1
            print(angle_constraint_in_degrees)
            effective_angle_in_degrees = 180 - angle_constraint_in_degrees
            effective_angle_in_radians = math.radians(effective_angle_in_degrees)
            raw_point_b = [math.cos(effective_angle_in_radians) * length_scale,
                           math.sin(effective_angle_in_radians) * length_scale]
            point_b = util.round_nums(raw_point_b)
            path_points = [point_a, origin, point_b]
        else:
            return angle_constraint_in_degrees

