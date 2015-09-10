"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the tube/pylon cost component of an edge
Last Modified: 8/15/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To implement a non naive tube/pylon cost method.
"""
# Standard Modules
from scipy.interpolate import PchipInterpolator

# Custom Modules
import match_landscape as landscape
import parameters
import util

def compute_pylon_cost(pylon_height):
    if pylon_height >= 0:
        height_cost = pylon_height * parameters.PYLON_COST_PER_METER
    else:
        height_cost = -pylon_height * 5 * parameters.PYLON_COST_PER_METER
    pylon_cost = parameters.PYLON_BASE_COST + height_cost
    return pylon_cost


def compute_tube_cost(tube_length):
    tube_cost = parameters.TUBE_COST_PER_METER * tube_length
    return tube_cost


def quick_build_tube_v1(elevation_profile):
    geospatials = [elevation_point["geospatial"] for elevation_point
                   in elevation_profile]
    land_elevations = [elevation_point["land_elevation"] for elevation_point
                       in elevation_profile]
    arc_lengths = [elevation_point["distance_along_path"] for elevation_point
                   in elevation_profile]
    s_interp, z_interp = landscape.match_landscape_v1(arc_lengths,
                                                      land_elevations, "elevation")
    tube_spline = PchipInterpolator(s_interp, z_interp)
    tube_elevations = tube_spline(arc_lengths)
    spatial_x_values, spatial_y_values = zip(*geospatials)
    pylon_heights = util.subtract(tube_elevations, land_elevations)
    tube_coords = zip(spatial_x_values, spatial_y_values, tube_elevations)
    tube_length = util.compute_total_arc_length(tube_coords)
    total_pylon_cost = sum(map(compute_pylon_cost, pylon_heights))
    total_tube_cost = compute_tube_cost(tube_length)
    return [total_tube_cost, total_pylon_cost, tube_elevations]

