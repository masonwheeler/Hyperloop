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
        point_arc_length = distance_along_edge + start_arc_length
        edge_arc_lengths.append(point_arc_length)
        point = distance_along_edge_to_point(edge, distance_along_edge)
        edge_points.append(point)
        distance_along_edge += sample_spacing
    distance_along_edge -= edge_length
    return [edge_points, edge_arc_lengths, distance_along_edge, edge_length]

def sample_edges(edges, sample_spacing):
    distance_along_edge = 0
    start_arc_length = 0
    points = []
    arc_lengths = []    
    for edge in edges:
        edge_points, edge_arc_lengths, distance_along_edge, edge_length = \
        sample_edge(edge, sample_spacing, distance_along_edge, start_arc_length)
        points += edge_points
        arc_lengths += edge_arc_lengths
        start_arc_length += edge_length
    last_arc_length = start_arc_length
    return [points, arc_lengths, last_arc_length]

def sample_path(path_points, path_sample_spacing):
    path_edges = points_to_edges(path_points)
    sampled_path_points, sampled_arc_lengths, last_arc_length = \
                    sample_edges(path_edges, path_sample_spacing)
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

