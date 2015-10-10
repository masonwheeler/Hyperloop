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

