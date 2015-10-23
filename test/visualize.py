"""
Original Developer: Jonathan Ward
Purpose of Module: To visualize the output from the algorithm.

Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To remove unnecessary functions and lines.
"""

# Standard Modules
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


PLOT_QUEUE_SPATIAL_2D = []
PLOT_QUEUE_SCATTERPLOT = []
ELEVATION_PROFILE_PLOT_QUEUE = []
CURVATURE_PROFILE_PLOT_QUEUE = []
SPEED_PROFILE_PLOT_QUEUE = []


def plot_object(object_data, style):
    x_values, y_values = object_data
    plt.plot(x_values, y_values, style)

def plot_3d_object(object_data, style):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x_values, y_values, z_values = object_data
    ax.plot(x_values, y_values, z_values)
    plt.show()

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

