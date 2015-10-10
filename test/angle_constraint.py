"""
Original Developer: 
    Jonathan Ward
"""

# Standard Modules:
import numpy as np

# Custom Modules:
import math
import config
import curvature
import sample_path

VISUALIZE_CONSTRAINT = False

def test_path_points(path_points, interpolator, max_curvature, resolution):
    sampled_path_points, arc_lengths = sample_path.sample_path_points(
                                                  path_points, resolution)
    interpolated_points, curvature_array = interpolator(sampled_path_points,
                                                                 resolution)
    is_curvature_acceptable = curvature.test_curvature_validity(
                                 curvature_array, max_curvature)
    if config.VISUAL_MODE and VISUALIZE_CONSTRAINT:
        import visualize
        path_points_x_vals, path_points_y_vals = zip(*path_points)  
        plottable_path_points = [path_points_x_vals, path_points_y_vals]
        plottable_path = [plottable_path_points, 'r-']    
        visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_path)
        interpolated_x_vals, interpolated_y_vals = np.transpose(
                                                interpolated_points)
        plottable_interpolated_points = [interpolated_x_vals,
                                         interpolated_y_vals]
        plottable_interpolation = [plottable_interpolated_points, 'b-']
        visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_interpolation)
        visualize.plot_objects(visualize.PLOT_QUEUE_SPATIAL_2D, False)
        visualize.PLOT_QUEUE_SPATIAL_2D.pop()
        visualize.PLOT_QUEUE_SPATIAL_2D.pop()
    return is_curvature_acceptable

def compute_angle_constraint(length_scale, interpolator, max_curvature,
                                                             max_error):
    origin = [0, 0]
    point_a = [length_scale, 0]
    angle_constraint_in_degrees = 0.1
    effective_angle_in_degrees = 180 - angle_constraint_in_degrees
    effective_angle_in_radians = math.radians(effective_angle_in_degrees)
    point_b = [math.cos(effective_angle_in_radians) * length_scale,
               math.sin(effective_angle_in_radians) * length_scale]
    path_points = [point_a, origin, point_b]
    while True:
        is_curvature_acceptable = test_path_points(path_points, interpolator,
                                                    max_curvature, max_error)
        if is_curvature_acceptable:
            angle_constraint_in_degrees += 0.1
            effective_angle_in_degrees = 180 - angle_constraint_in_degrees
            effective_angle_in_radians = math.radians(effective_angle_in_degrees)
            point_b = [math.cos(effective_angle_in_radians) * length_scale,
                       math.sin(effective_angle_in_radians) * length_scale]
            path_points = [point_a, origin, point_b]
        else:
            return angle_constraint_in_degrees

