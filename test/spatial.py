"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To provide an abstraction for handling all spatial aspects of the program

Last Modified: 
    9/8/15

Last Modified By:
    Jonathan Ward

Last Modification Purpose:
    Created Module
"""

import config
import directions
import spatial_lattice
import spatial_edges
import spatial_graphs
import spatial_interpolate
import spatial_paths_2d
import spatial_paths_3d

if config.VISUAL_MODE:
    import visualize
    VISUALIZE_DIRECTIONS = True
    VISUALIZE_SPLINE = True
    VISUALIZE_LATTICE = True
    VISUALIZE_EDGES = True
    VISUALIZE_GRAPHS = True
    VISUALIZE_COST_TIME_SCATTERPLOT = True
    VISUALIZE_PATHS_2D = True
    VISUALIZE_PATHS_3D = True

def build_directions(start, end):
    """Build Directions Object
    """
    route_directions = directions.get_directions(start, end)
    config.PROJ = route_directions.projection
    return route_directions

def build_spatial_lattice(route_directions):
    """Build lattice between directions points and spline points
    """
    route_spatial_lattice = spatial_lattice.get_spatial_lattice(
                                             route_directions, 9, 7)
    if config.VISUAL_MODE:
        if VISUALIZE_SPLINE:
            plottable_spline = route_spatial_lattice.get_plottable_spline('r-')
            config.PLOT_QUEUE_SPATIAL_2D.append(plottable_spline)
        if VISUALIZE_DIRECTIONS:
            plottable_directions = \
                route_spatial_lattice.get_plottable_directions('b-')
            config.PLOT_QUEUE_SPATIAL_2D.append(plottable_directions)
        if VISUALIZE_LATTICE:
            plottable_lattice = route_spatial_lattice.get_plottable_lattice('g.')
            config.PLOT_QUEUE_SPATIAL_2D.append(plottable_lattice)
    return route_spatial_lattice

def build_spatial_edges_sets(route_spatial_lattice):
    """Build edges between pairs of a lattice points
    """
    route_spatial_edges_sets = spatial_edges.get_spatial_edges_sets(
                                              route_spatial_lattice,
                                        spatial_interpolate.quintic)
    if config.VISUAL_MODE:
        if VISUALIZE_EDGES:
            plottable_edges = route_spatial_edges_sets.get_plottable_edges('k-')
            config.PLOT_QUEUE_SPATIAL_2D += plottable_edges
    return route_spatial_edges_sets

def build_spatial_graphs_sets(route_spatial_edges_sets):
    """Build graphs from edges
    """
    route_spatial_graphs_sets = spatial_graphs.get_spatial_graphs_sets(
                                                 route_spatial_edges_sets)
    if config.VISUAL_MODE:
        if VISUALIZE_GRAPHS:
            plottable_graphs = route_spatial_graphs_sets.get_plottable_graphs()
            for plottable_graph in plottable_graphs:
                config.PLOT_QUEUE.append([plottable_graph, 'c-'])
                visualize.plot_objects(config.PLOT_QUEUE)
                config.PLOT_QUEUE.pop()
        if VISUALIZE_COST_TIME_SCATTERPLOT:
            cost_time_scatter = route_spatial_graphs_sets.cost_time_scatter()
            config.PLOT_QUEUE_COST_TIME_SCATTERPLOT.append(
                                     [cost_time_scatter, 'r.'])
            visualize.plot_objects(config.PLOT_QUEUE_COST_TIME_SCATTERPLOT)
    return route_spatial_graphs_sets

def build_spatial_paths_set_2d(route_spatial_graphs_sets):
    """Interpolate full length spatial graphs
    """
    route_spatial_paths_set_2d = spatial_paths_2d.get_spatial_paths_set_2d(
                                                 route_spatial_graphs_sets)
    if config.VISUAL_MODE:
        if VISUALIZE_PATHS_2D:
            plottable_paths_2d = \
                route_spatial_paths_set_2d.get_plottable_paths()
            plottable_paths_graphs_2d = \
                route_spatial_paths_set_2d.get_paths_graphs()
            plottable_paths_and_graphs = zip(plottable_paths_2d,
                                             plottable_paths_graphs_2d)
            for plottable_path_and_graph in plottable_paths_and_graphs:
                plottable_path, plottable_graph = plottable_path_and_graph
                config.PLOT_QUEUE_SPATIAL_2D.append([plottable_path, 'c-'])
                config.PLOT_QUEUE_SPATIAL_2D.append([plottable_graph, 'y-'])
                visualize.plot_objects(config.PLOT_QUEUE_SPATIAL_2D)
                config.PLOT_QUEUE_SPATIAL_2D.pop()
                config.PLOT_QUEUE_SPATIAL_2D.pop()
    return route_spatial_paths_set_2d

def build_spatial_paths_3d(route_spatial_paths_set_2d):
    """Build the best tube elevation options for a given 2d spatial path
    """
    route_spatial_paths_set_3d = spatial_paths_2d.get_spatial_paths_2d(
                                            route_spatial_paths_set_2d)
    if config.VISUAL_MODE:
        if VISUALIZE_PATHS_3D:
            plottable_paths_3d = \
                route_spatial_paths_set_3d.get_plottable_paths()            
    return route_spatial_paths_set_3d

def city_pair_to_spatial_graphs_sets(start, end):
    route_directions = build_directions(start, end)
    route_spatial_lattice = build_spatial_lattice(route_directions)
    route_spatial_edges_sets = build_spatial_edges_sets(route_spatial_lattice)
    route_spatial_graphs_sets = build_spatial_graphs_sets(
                                     route_spatial_edges_sets)
    route_spatial_paths_set_2d = build_spatial_paths_set_2d(
                                     route_spatial_graphs_sets)
    #route_spatial_paths_3d = build_spatial_paths_3d(route_spatial_paths_set_2d)
    return route_spatial_graphs_sets

