"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the tube/pylon cost component of an edge
Last Modified: 8/15/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To implement a non naive tube/pylon cost method.
"""

# Custom Modules
import config
import parameters
import trip_time
import tube_interpolate
import util
import visualize

VISUALIZE_TUBE = True
PLOT_QUEUE_ELEVATION_PROFILE = []

def compute_pylon_cost(pylon_height):
    if pylon_height >= 0:
        height_cost = pylon_height * parameters.PYLON_COST_PER_METER
    else:
        height_cost = -pylon_height * 5 * parameters.PYLON_COST_PER_METER
    pylon_cost = parameters.PYLON_BASE_COST + height_cost
    return pylon_cost

def compute_tube_cost(tube_coords):
    tube_length = util.compute_total_arc_length(tube_coords)
    tube_cost = parameters.TUBE_COST_PER_METER * tube_length
    return tube_cost

def quick_build_tube(elevation_profile, tube_interpolator):
    geospatials = [elevation_point["geospatial"] for elevation_point
                   in elevation_profile]
    land_elevations = [elevation_point["land_elevation"] for elevation_point
                       in elevation_profile]
    arc_lengths = [elevation_point["distance_along_path"] for elevation_point
                   in elevation_profile]
    arc_length_waypoints, tube_elevation_waypoints = \
        tube_interpolate.get_tube_waypoints_v1(arc_lengths, land_elevations)
    tube_elevations, tube_curvature = tube_interpolate.tube_pchip(
         arc_length_waypoints, tube_elevation_waypoints, arc_lengths)
    time = trip_time.compute_time(tube_curvature, arc_lengths)
    spatial_x_values, spatial_y_values = zip(*geospatials)
    pylon_heights = util.subtract(tube_elevations, land_elevations)
    total_pylon_cost = sum(map(compute_pylon_cost, pylon_heights))
    tube_coords = zip(spatial_x_values, spatial_y_values, tube_elevations)
    total_tube_cost = compute_tube_cost(tube_coords)
    if config.VISUAL_MODE and VISUALIZE_TUBE:
        land_elevation_points = [arc_lengths, land_elevations]
        plottable_land_elevation = [land_elevation_points, 'r-']
        PLOT_QUEUE_ELEVATION_PROFILE.append(plottable_land_elevation)
        tube_elevation_points = [arc_lengths, tube_elevations]
        plottable_tube_elevation = [tube_elevation_points, 'b-']
        PLOT_QUEUE_ELEVATION_PROFILE.append(plottable_tube_elevation)
        are_axes_equal = False
        print("total tube cost: " + str(total_tube_cost))
        print("total pylon cost: " + str(total_pylon_cost))
        visualize.plot_objects(PLOT_QUEUE_ELEVATION_PROFILE, are_axes_equal)        
        PLOT_QUEUE_ELEVATION_PROFILE.pop()
        PLOT_QUEUE_ELEVATION_PROFILE.pop()
    return [total_tube_cost, total_pylon_cost, time]

