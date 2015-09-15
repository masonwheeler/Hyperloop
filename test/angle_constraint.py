"""
Original Developer: 
    Jonathan Ward
"""

import math

import curvature
import util


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

def test_path_points_v2(path_points, max_curvature):
    naive_curvature = curvature.compute_naive_curvature(path_points)
    is_curvature_acceptable = naive_curvature < max_curvature
    return is_curvature_acceptable

def test_path_points_v3(path_points, interpolator, max_curvature):
    naive_curvature = curvature.compute_naive_curvature(path_points)
    is_curvature_acceptable = naive_curvature < max_curvature
    return is_curvature_acceptable

def compute_degree_constraint(length_scale, max_curvature):
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
        is_curvature_acceptable = test_path_points_v2(path_points,
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

