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
import config
import util
import visualize
import cacher
import directions
import proj
import lattice
import edges
import graphs
import interpolate
import routes


def build_directions(start, end):
    """Fetch Google driving directions.
    """
    directions_lat_lngs = directions.get_directions(start, end)
    start_lat_lng, end_lat_lng = util.get_firstlast(directions_lat_lngs)
    proj.set_projection(start_lat_lng, end_lat_lng)
    directions_geospatials = proj.latlngs_to_geospatials(directions_lat_lngs,
                                                                 config.PROJ)
    return [directions_geospatials, start_lat_lng, end_lat_lng]


def build_lattice(directions_geospatials):
    """Build lattice between directions points and spline points
    """
    time_a = time.time()
    spatial_lattice = lattice.SpatialLattice(directions_geospatials, 9, 7)
    time_b = time.time()
    print "Building the lattice took " + str(time_b - time_a) + " seconds."
    if config.VISUAL_MODE:
        plottable_spline = spatial_lattice.get_plottable_spline()
        config.PLOT_QUEUE.append([plottable_spline, 'r-'])        
        plottable_directions = spatial_lattice.get_plottable_directions()
        config.PLOT_QUEUE.append([plottable_directions, 'b-'])
        plottable_lattice = spatial_lattice.get_plottable_lattice()
        config.PLOT_QUEUE.append([plottable_lattice, 'g.'])
    return spatial_lattice


def build_graphs(spatial_lattice):
    """Build graph skeletons from lattice slices
    """
    time_a = time.time()
    spatial_edges_sets = edges.SpatialEdgesSets(spatial_lattice)
    time_b = time.time()
    print "Building the graphs took " + str(time_b - time_a) + " seconds."
    if config.VISUAL_MODE:
        plottable_graphs = [graph.to_plottable(
            'b-') for graph in complete_graphs]
        #costs = [graph.pylon_cost + graph.land_cost for graph
        #                                   in complete_graphs]
        #curvatures = [graph.curvature_metric for graph in complete_graphs]
        # cost_curvature = [graph.plot_costcurvature() for graph
        #                in complete_graphs]
        #costs, curvatures = zip(*cost_curvature)
        #visualize.scatter_plot(costs, curvatures)
        # print(plottable_cost_curvature)
        config.PLOT_QUEUE += plottable_graphs
        #config.PLOT_QUEUE += plottable_cost_curvature
    return 0 #complete_graphs


def pair_analysis(start, end):
    """Builds routes between start and end points
    """
    cacher.create_necessaryfolders(start, end)
    time_a = time.time()
    directions_geospatials, start_lat_lng, end_lat_lng = build_directions(
        start, end)
    spatial_lattice = build_lattice(directions_geospatials)    
    complete_graphs = build_graphs(spatial_lattice)
    """
    test_graphs = complete_graphs[:3]
    complete_routes = [routes.graph_to_route(graph,
                      config.LINEAR_ACCEL_CONSTRAINT/config.MAX_SPEED**2,
                      config.LINEAR_ACCEL_CONSTRAINT, config.JERK_TOL)
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
    """
    if config.VISUAL_MODE:
        visualize.plot_objects(config.PLOT_QUEUE)    
    return 0
