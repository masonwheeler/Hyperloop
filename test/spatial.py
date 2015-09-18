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
import tube
import util

if config.VISUAL_MODE:
    import visualize
    VISUALIZE_DIRECTIONS = False
    VISUALIZE_SPLINE = False
    VISUALIZE_LATTICE = False
    VISUALIZE_EDGES = True
    VISUALIZE_GRAPHS = False
    VISUALIZE_COST_TIME_SCATTERPLOT = False
    VISUALIZE_PATHS_2D = False
    VISUALIZE_PATHS_3D = True

def build_directions(start, end):
    """Build Directions Object
    """
    route_directions = directions.get_directions(start, end)
    #route_directions = directions.Directions.get_directions(start, end)
    return route_directions

def build_spatial_lattice(route_directions):
    """Build lattice between directions points and spline points
    """
    route_spatial_lattice = spatial_lattice.get_spatial_lattice(
                                             route_directions, 6, 4)
    util.smart_print("With a base resolution of: " +
                str(route_spatial_lattice.SPATIAL_BASE_RESOLUTION)+ " meters.")
    util.smart_print("The spatial lattice spacing parallel to the route is: " +
                     str(route_spatial_lattice.spatial_x_spacing) + " meters.")
    util.smart_print("And perpendicular to the route is: " +
                     str(route_spatial_lattice.spatial_y_spacing) + " meters.")
    if config.VISUAL_MODE:
        if VISUALIZE_SPLINE:
            plottable_spline = route_spatial_lattice.get_plottable_spline('r-')
            visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_spline)
        if VISUALIZE_DIRECTIONS:
            plottable_directions = \
                route_spatial_lattice.get_plottable_directions('b-')
            visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_directions)
        if VISUALIZE_LATTICE:
            plottable_lattice = route_spatial_lattice.get_plottable_lattice('g.')
            visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_lattice)
    return route_spatial_lattice

def build_spatial_edges_sets(route_spatial_lattice):
    """Build edges between pairs of a lattice points
    """
    route_spatial_edges_sets = spatial_edges.get_spatial_edges_sets(
                                              route_spatial_lattice,
                                spatial_interpolate.scipy_smoothing,
                                              tube.quick_build_tube)
    if not route_spatial_edges_sets.TUBE_READY:
        route_spatial_edges_sets.build_tubes()
    if config.VISUAL_MODE:
        if VISUALIZE_EDGES:
            plottable_edges = route_spatial_edges_sets.get_plottable_edges('k-')
            visualize.PLOT_QUEUE_SPATIAL_2D += plottable_edges
    return route_spatial_edges_sets

def build_spatial_graphs_sets(route_spatial_edges_sets):
    """Build graphs from edges
    """
    route_spatial_graphs_sets = spatial_graphs.get_spatial_graphs_sets(
                                                 route_spatial_edges_sets)
    if config.VISUAL_MODE:
        if VISUALIZE_GRAPHS:
            plottable_graphs = route_spatial_graphs_sets.get_plottable_graphs('c-')
            are_axes_equal = True
            for plottable_graph in plottable_graphs:
                visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_graph)
                visualize.plot_objects(visualize.PLOT_QUEUE_SPATIAL_2D,
                                       are_axes_equal)
                visualize.PLOT_QUEUE_SPATIAL_2D.pop()
        if VISUALIZE_COST_TIME_SCATTERPLOT:
            are_axes_equal = False
            cost_time_scatterplot = \
                route_spatial_graphs_sets.get_cost_time_scatterplot('r.')
            visualize.PLOT_QUEUE_SCATTERPLOT.append(cost_time_scatterplot)
            visualize.plot_objects(visualize.PLOT_QUEUE_SCATTERPLOT,
                                   are_axes_equal)
    return route_spatial_graphs_sets

def build_spatial_paths_set_2d(route_spatial_graphs_sets):
    """Interpolate full length spatial graphs
    """
    route_spatial_paths_set_2d = spatial_paths_2d.get_spatial_paths_set_2d(
                                                 route_spatial_graphs_sets)
    if config.VISUAL_MODE:
        if VISUALIZE_PATHS_2D:
            plottable_paths_2d = \
                route_spatial_paths_set_2d.get_plottable_paths('c-')
            plottable_paths_graphs_2d = \
                route_spatial_paths_set_2d.get_plottable_graphs('y-')
            plottable_paths_and_graphs = zip(plottable_paths_2d,
                                             plottable_paths_graphs_2d)
            are_axes_equal = True
            for plottable_path_and_graph in plottable_paths_and_graphs:
                plottable_path, plottable_graph = plottable_path_and_graph
                visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_path)
                visualize.PLOT_QUEUE_SPATIAL_2D.append(plottable_graph)
                visualize.plot_objects(visualize.PLOT_QUEUE_SPATIAL_2D,
                                       are_axes_equal)
                visualize.PLOT_QUEUE_SPATIAL_2D.pop()
                visualize.PLOT_QUEUE_SPATIAL_2D.pop()
    return route_spatial_paths_set_2d

def build_spatial_paths_3d(route_spatial_paths_set_2d):
    """Build the best tube elevation options for a given 2d spatial path
    """
    route_spatial_paths_sets_3d = spatial_paths_3d.get_spatial_paths_sets_3d(
                                                  route_spatial_paths_set_2d)
    if config.VISUAL_MODE:
        if VISUALIZE_PATHS_3D:
            plottable_paths_3d = \
                route_spatial_paths_set_3d.get_plottable_paths()            
    return route_spatial_paths_set_3d

"""
def city_pair_to_spatial_graphs_sets(start, end):
    route_directions = build_directions(start, end)
    route_spatial_lattice = build_spatial_lattice(route_directions)
    route_spatial_edges_sets = build_spatial_edges_sets(route_spatial_lattice)
    route_spatial_graphs_sets = build_spatial_graphs_sets(
                                     route_spatial_edges_sets)
    if config.VISUAL_MODE:
        are_axes_equal = True
        visualize.plot_objects(visualize.PLOT_QUEUE_SPATIAL_2D, are_axes_equal)
    return route_spatial_graphss_sets
"""

def city_pair_to_spatial_paths_set_2d(start, end):
    route_directions = build_directions(start, end)
    route_spatial_lattice = build_spatial_lattice(route_directions)
    route_spatial_edges_sets = build_spatial_edges_sets(route_spatial_lattice)
    route_spatial_graphs_sets = build_spatial_graphs_sets(
                                     route_spatial_edges_sets)
    route_spatial_paths_set_2d = build_spatial_paths_set_2d(
                                      route_spatial_graphs_sets)
    route_spatial_paths_3d = build_spatial_paths_3d(route_spatial_paths_set_2d)
    if config.VISUAL_MODE:
        are_axes_equal = True
        visualize.plot_objects(visualize.PLOT_QUEUE_SPATIAL_2D, are_axes_equal)
    return route_spatial_paths_set_2d
