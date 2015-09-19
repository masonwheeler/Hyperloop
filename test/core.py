"""
Original Developer: Jonathan Ward
Purpose of Module: To perform the core computations for each city pair.
Last Modified: 8/29/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To validate using pylint
"""

#pylint: disable=W0142

# Standard Modules:
import time

# Our Modules:
import cacher
import config
import saver
import spatial
import parameters
import routes
import visualize


def pair_analysis(start, end):
    """Builds routes between start and end points
    """
    cacher.create_necessaryfolders(start, end)
    time_a = time.time()
    spatial_paths_set_3d = spatial.city_pair_to_spatial_paths_set_3d(start, end)
    spatial_paths_3d = spatial_paths_set_3d.selected_paths
    start = spatial_paths_set_3d.start
    end = spatial_paths_set_3d.end
    start_latlng = spatial_paths_set_3d.start_latlng
    end_latlng = spatial_paths_set_3d.end_latlng
    print("num paths: " + str(len(spatial_paths_3d)))
    complete_routes = [routes.spatial_path_3d_to_route(spatial_path_3d)
                       for spatial_path_3d in spatial_paths_3d]
    #complete_routes = [routes.path_to_route(path) for path in spatial_paths_2d]
    #complete_routes = [routes.graph_to_route(graph,
    #                  parameters.MAX_LINEAR_ACCEL/parameters.MAX_SPEED**2,        
    #                  parameters.MAX_LINEAR_ACCEL, config.JERK_TOL)       
    #                  for graph in spatial_graphs]
    #saver.save_routes(complete_routes, start, end, start_latlng, end_latlng)
    """
    index = 1
    for route in complete_routes:
        print ("(triptime, comfort rating, pylon cost, tube cost, land cost) \
                of route "+ index +" is:" +
                str([route.trip_time,
                     route.comfort_rating,
                     route.pylon_cost,
                     route.tube_cost,
                     route.land_cost]))
        index += 1
    """
    time_b = time.time()
    print "City pair analysis took " + str(time_b - time_a) + " seconds."
    return 0
