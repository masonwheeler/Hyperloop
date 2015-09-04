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
# import match_landscape as match
# import advanced_interpolate as interp
import routes


def build_directions(start, end):
    """Fetch Google driving directions.
    """
    directions_lat_lngs = directions.get_directions(start, end)
    start_lat_lng, end_lat_lng = util.get_firstlast(directions_lat_lngs)
    proj.set_projection(start_lat_lng, end_lat_lng)
    directions_geospatials = proj.latlngs_to_geospatials(directions_lat_lngs,
                                                                 config.PROJ)
    #if config.VISUAL_MODE:
    #    plottable_directions = [zip(*directions_geospatials), 'y-']
    #    config.PLOT_QUEUE.append(plottable_directions)
    return [directions_geospatials, start_lat_lng, end_lat_lng]


def build_lattice(directions_geospatials):
    """Build lattice between directions points and spline points
    """
    #time_a = time.time()
    """
    sampled_points = interpolate.sample_path(directions_points,
                                             config.DIRECTIONS_SAMPLE_SPACING)
    s_values = interpolate.get_s_values(len(sampled_points))
    spatial_x_spline, spatial_y_spline = lattice.get_directionsspline(
        sampled_points)
    spatial_lattice_slices_s_values = interpolate.get_slice_s_values(s_values,
                                       config.SPATIAL_SLICE_S_VALUE_STEP_SIZE)
    spatial_slices_x_values = interpolate.get_spline_values(
        spatial_x_spline, spatial_lattice_slices_s_values)
    spatial_slices_y_values = interpolate.get_spline_values(
        spatial_y_spline, spatial_lattice_slices_s_values)
    spatial_spline_tuples = zip(spatial_slices_x_values,
                                spatial_slices_y_values)
    spatial_spline_points = [list(eachTuple) for eachTuple in
                             spatial_spline_tuples]
    slices_directions_points = util.smart_sample_nth_points(
        sampled_points, config.SPATIAL_SLICE_S_VALUE_STEP_SIZE)
    spatial_slices_bounds = zip(slices_directions_points,
                                spatial_spline_points)
    lattice_slices = lattice.get_lattice(spatial_slices_bounds)
    """
    #lattice = lattice.get_spatial_lattice(directions_geospatials)
    spatial_lattice = lattice.SpatialLattice(directions_geospatials, 9, 7)
    #time_b = time.time()
    #print "Building the lattice took " + str(time_b - time_a) + " seconds."
    if config.VISUAL_MODE:
        plottable_spline = spatial_lattice.get_plottable_spline()
        config.PLOT_QUEUE.append([plottable_spline, 'r-'])        
        plottable_directions = spatial_lattice.get_plottable_directions()
        config.PLOT_QUEUE.append([plottable_directions, 'b-'])
        plottable_lattice = spatial_lattice.get_plottable_lattice()
        config.PLOT_QUEUE.append([plottable_lattice, 'g.'])
    return spatial_lattice

# config.DEGREE_CONSTRAINT = min(math.fabs(math.pi - math.acos(min((
# config.distance_btwn_slices*(config.G_TOLERANCE/330**2))**2/2-1,1))),
# math.pi)*(180./math.pi)


def build_graphs(spatial_lattice):
    """Build graph skeletons from lattice slices
    """
    time_a = time.time()
    #finished_edges_sets = edges.get_edgessets(lattice_slices)
    spatial_edges_sets = edges.SpatialEdgesSets(spatial_lattice)
    #final_edges_sets = edges.get_spatial_edges_sets(spatial_lattice)
    # for edges_set in finished_edges_sets:
    #    for edge in edges_set:
    #        print("edge geospatials: " + str(edge.geospatials))
    #        time.sleep(10)
    #t2 = time.time()
    # edges.build_pylons(finished_edges_sets)
    #t3 = time.time()
    #print("Building the pylons took " + str(t3 - t2) + " seconds.")
    #spatial_graphs = graphs.build_spatial_graphs(final_edges_sets)
    #complete_graphs = graphs.get_graphs(final_edges_sets)
    #print("len complete graphs: " + str(len(complete_graphs)))
    #print("graphs num edges: " + str(complete_graphs[0].num_edges))
    # graph_geospatials = [tuple(map(tuple, graph.geospatials[:-1]))
    #                    for graph in complete_graphs]
    # print(graph_geospatials[0])
    # print(len(graph_geospatials))
    # print(len(set(graph_geospatials)))
    # for graph in complete_graphs:
    #    print("geospatials: " + str(graph.geospatials))
    #    print("pylon cost: " + str(graph.pylon_cost))
    #    print("land cost : " + str(graph.land_cost))
    #    print("curvature: " + str(graph.curvature_metric))
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
    return complete_graphs


def pair_analysis(start, end):
    """Builds routes between start and end points
    """
    cacher.create_necessaryfolders(start, end)
    time_a = time.time()
    directions_geospatials, start_lat_lng, end_lat_lng = build_directions(
        start, end)
    spatial_lattice = build_lattice(directions_geospatials)    
    #complete_graphs = build_graphs(spatial_lattice)
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
