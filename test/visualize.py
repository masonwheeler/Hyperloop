"""
Original Developer: Jonathan Ward
Purpose of Module: To visualize the output from the algorithm.

Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To remove unnecessary functions and lines.
"""

# Standard Modules
import matplotlib.pyplot as plt
import numpy as np

# Our Modules
import config
import interpolate
import util


def circle_function(x, r):
    if x > r:
        return -float("Inf")
    else:
        y = np.sqrt(np.square(r) - np.square(x)) - r
        return y


def build_window(left_bound, right_bound, radius):
    relative_indices = range(-left_bound, right_bound + 1)
    window = [{"relative_index": relative_index,
               "relative_elevation":
               circle_function(abs(relative_index * config.PYLON_SPACING), radius)}
              for relative_index in relative_indices]
    return window


def add_current_window(envelope, current_window):
    for point in current_window:
        current_index = point["index"]
        envelope[current_index].append(point["elevation"])


def build_envelope(elevations, radius):
    window_size = int(radius / config.PYLON_SPACING)
    envelope_lists = [[] for i in xrange(len(elevations))]
    for current_index in range(0, len(elevations)):
        if current_index < window_size:
            left_bound = current_index
        else:
            left_bound = window_size
        if current_index > (len(elevations) - 1) - window_size:
            right_bound = (len(elevations) - 1) - current_index
        else:
            right_bound = window_size
        relative_window = build_window(left_bound, right_bound, radius)
        current_elevation = elevations[current_index]
        current_window = [{
            "index": point["relative_index"] + current_index,
            "elevation": point["relative_elevation"] + current_elevation
        }
            for point in relative_window]
        add_current_window(envelope_lists, current_window)
    envelope = map(max, envelope_lists)
    return envelope


def visualize_elevation_profile(elevation_profile):
    distances = []
    elevations = []
    num_points = len(elevation_profile)
    s_values = np.arange(num_points)
    for elevation_point in elevation_profile:
        distance = elevation_point["distance_along_path"]
        elevation = elevation_point["land_elevation"]
        distances.append(distance)
        elevations.append(elevation)
    curvature_threshold_a = interpolate.compute_curvature_threshold(
        config.max_speed, config.VERTICAL_ACCEL_CONSTRAINT)
    radius_a = 1.0 / curvature_threshold_a
    envelope_a = build_envelope(elevations, radius_a)
    curvature_threshold_b = interpolate.compute_curvature_threshold(
        config.max_speed / 1.2, config.VERTICAL_ACCEL_CONSTRAINT)
    radius_b = 1.0 / curvature_threshold_b
    envelope_b = build_envelope(elevations, radius_b)
    plt.plot(distances, elevations)
    plt.plot(distances, envelope_a, 'r-')
    plt.plot(distances, envelope_b, 'g-')
    # plt.axis('equal')
    plt.show()


def visualize_elevation_profile_v2(elevation_profile, tube_elevations):
    distances = []
    land_elevations = []
    num_points = len(elevation_profile)
    s_values = np.arange(num_points)
    for elevation_point in elevation_profile:
        distance = elevation_point["distance_along_path"]
        land_elevation = elevation_point["land_elevation"]
        distances.append(distance)
        land_elevations.append(land_elevation)
    plt.plot(distances, land_elevations)
    plt.plot(distances, tube_elevations, 'r-')
    # plt.axis('equal')
    plt.show()


def plot_object(object_data, style):
    x_values, y_values = object_data
    #print(x_values, y_values, style)
    plt.plot(x_values, y_values, style)


def plot_objects(objects):
    for each_object in objects:
        object_data, object_style = each_object
        plot_object(object_data, object_style)
    # plt.axis('equal')
    plt.show()


def plot_colorful_objects(objects_and_styles):
    for each_object_and_style in objects_and_styles:
        each_object, each_style = each_object_and_style
        plot_object(each_object, each_style)
    plt.show()


def plot_objectslist(object_data, style):
    for each_object_data in object_data:
        plot_object(each_object_data, style)


def scatter_plot(x_vals, y_vals):
    plt.scatter(x_vals, y_vals)
    plt.show()


def display_inputs(inputs):
    for each_input in inputs:

        plot_function = function_dictionary[function_number]
        plot_function(object_data, style)
    # plt.subplot(plot_dictionary[1])
    # plt.subplot(plot_dictionary[2])
    # plt.axis('equal')
    #x1, x2, y1, y2 = plt.axis()
    #plt.axis((x1,x2, -10**(-4), 10**(-4)))
    plt.show()
