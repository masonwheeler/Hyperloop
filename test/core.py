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
import spatial
import parameters
import routes


def pair_analysis(start, end):
    """Builds routes between start and end points
    """
    cacher.create_necessaryfolders(start, end)
    time_a = time.time()
    spatial_graphs_sets = spatial.city_pair_to_spatial_graphs_sets(start, end)
    spatial_graphs = spatial_graphs_sets.selected_graphs
    test_graphs = spatial_graphs[:3]
    complete_routes = [routes.graph_to_route(graph,
                      parameters.MAX_LINEAR_ACCEL/parameters.MAX_SPEED**2,
                      parameters.MAX_LINEAR_ACCEL, config.JERK_TOL)
                      for graph in test_graphs]    
    cacher.save_routes(complete_routes, start, end, start_lat_lng, end_lat_lng)
    for i in range(len(complete_routes)):
        print ("(triptime, comfort rating, pylon cost, tube cost, land cost) \
                of route "+ str(i) +" is:" +
                str([complete_routes[i].trip_time,
                     complete_routes[i].comfort_rating,
                     complete_routes[i].pylon_cost,
                     complete_routes[i].tube_cost,
                     complete_routes[i].land_cost]))
    time_b = time.time()
    print "City pair analysis took " + str(time_b - time_a) + " seconds."
    if config.VISUAL_MODE:
        visualize.plot_objects(config.PLOT_QUEUE)    
    return 0
