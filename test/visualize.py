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

PLOT_QUEUE_SPATIAL_2D = []
PLOT_QUEUE_SCATTERPLOT = []

def visualize_elevation_profile(elevation_profile, tube_elevations):
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
    plt.plot(x_values, y_values, style)

def plot_objects(objects, are_axes_equal):
    for each_object in objects:
        object_data, object_style = each_object
        plot_object(object_data, object_style)
    if are_axes_equal:
        plt.axis('equal')
    plt.show()

def scatter_plot(x_vals, y_vals):
    plt.scatter(x_vals, y_vals)
    plt.show()

