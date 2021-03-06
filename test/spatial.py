"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To provide an abstraction for handling all spatial aspects of the program

Last Modified:
    11/02/15

Last Modified By:
    Mason Wheeler

Last Modification Purpose:
    Adding alternate route functionality
"""

import config
import directions
import spatial_lattice
import spatial_edges
import spatial_graphs
import smoothing_interpolate
import spatial_paths_2d
import spatial_paths_3d
import tube_naive
import util


if config.VISUAL_MODE:
    import visualize
    VISUALIZE_DIRECTIONS = False
    VISUALIZE_SPLINE = False
    VISUALIZE_LATTICE = False
    VISUALIZE_EDGES = False
    VISUALIZE_GRAPHS = False
    VISUALIZE_GRAPHS_COST_TIME_SCATTERPLOT = False
    VISUALIZE_PATHS_2D = False
    VISUALIZE_PATHS_3D_ELEVATIONS = False
    VISUALIZE_PATHS_COST_TIME_SCATTERPLOT = False


def build_directions(start, end):
    """Build Directions Object
    """
    route_directions = directions.get_directions(start, end)
    return route_directions.values

def build_spatial_lattice(route_directions):
    """Build lattice between directions points and spline points
    """
    route_spatial_lattice = spatial_lattice.get_spatial_lattice(
                                             route_directions, 6, 4)
    if config.VISUAL_MODE:
        util.smart_print("With a base resolution of: " +
            str(route_spatial_lattice.SPATIAL_BASE_RESOLUTION)+ " meters.")
        util.smart_print("The resolution parallel to the right of way is: " +
            str(route_spatial_lattice.parallel_resolution) + " meters.")
        util.smart_print("The resolution transverse to the right of way is: " +
            str(route_spatial_lattice.transverse_resolution) + " meters.")
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
          smoothing_interpolate.bounded_curvature_graph_interpolate,
                                        tube_naive.NaiveTubeProfile)
    if route_spatial_edges_sets != None:
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
        if VISUALIZE_GRAPHS_COST_TIME_SCATTERPLOT:
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
                route_spatial_paths_set_2d.get_plottable_paths('k-')
            plottable_paths_graphs_2d = \
                route_spatial_paths_set_2d.get_plottable_graphs('m-')
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
        if VISUALIZE_PATHS_3D_ELEVATIONS:
            for path_3d in route_spatial_paths_sets_3d.selected_paths:
                are_axes_equal = False
                plottable_tube_curvature = \
                    path_3d.get_plottable_tube_curvature('g')
                plottable_spatial_curvature = \
                    path_3d.get_plottable_spatial_curvature('y')
                plottable_tube_elevations = \
                    path_3d.get_plottable_tube_elevations('r')
                plottable_land_elevations = \
                    path_3d.get_plottable_land_elevations('b')
                visualize.CURVATURE_PROFILE_PLOT_QUEUE.append(
                                        plottable_tube_curvature)
                visualize.CURVATURE_PROFILE_PLOT_QUEUE.append(
                                        plottable_spatial_curvature)
                visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                                        plottable_tube_elevations)
                visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                                        plottable_land_elevations)
                visualize.plot_objects(visualize.CURVATURE_PROFILE_PLOT_QUEUE,
                                       are_axes_equal)
                visualize.plot_objects(visualize.ELEVATION_PROFILE_PLOT_QUEUE,
                                       are_axes_equal)
                visualize.CURVATURE_PROFILE_PLOT_QUEUE.pop()
                visualize.CURVATURE_PROFILE_PLOT_QUEUE.pop()
                visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
                visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
        if VISUALIZE_PATHS_COST_TIME_SCATTERPLOT:
            are_axes_equal = False
            cost_time_scatterplot = \
                route_spatial_paths_sets_3d.get_cost_time_scatterplot('g.')
            visualize.PLOT_QUEUE_SCATTERPLOT.append(cost_time_scatterplot)
            visualize.plot_objects(visualize.PLOT_QUEUE_SCATTERPLOT,
                                   are_axes_equal)
    return route_spatial_paths_sets_3d

def city_pair_to_paths_3d(start, end):
    result = []
    for route_directions in build_directions(start, end):
        route_spatial_lattice = build_spatial_lattice(route_directions)
        route_spatial_edges_sets = build_spatial_edges_sets(route_spatial_lattice)
        route_spatial_graphs_sets = build_spatial_graphs_sets(
                                         route_spatial_edges_sets)
        route_spatial_paths_set_2d = build_spatial_paths_set_2d(
                                          route_spatial_graphs_sets)
        route_spatial_paths_sets_3d = build_spatial_paths_3d(
                                      route_spatial_paths_set_2d)
        if config.VISUAL_MODE:
            if len(visualize.PLOT_QUEUE_SPATIAL_2D) > 0:
                are_axes_equal = True
                visualize.plot_objects(visualize.PLOT_QUEUE_SPATIAL_2D, are_axes_equal)
                                       are_axes_equal)
        result.append(route_spatial_paths_sets_3d)
    return result

