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


def build_directions(start, end):
    """Build Directions Object
    """
    route_directions = directions.get_directions(start, end)
    return route_directions

def build_spatial_lattice(route_directions):
    """Build lattice between directions points and spline points
    """    
    route_spatial_lattice = spatial_lattice.get_spatial_lattice(
                                             route_directions, 9, 7)
    if config.VISUAL_MODE:
        plottable_spline = route_spatial_lattice.get_plottable_spline()
        config.PLOT_QUEUE.append([plottable_spline, 'r-'])
        plottable_directions = route_spatial_lattice.get_plottable_directions()
        config.PLOT_QUEUE.append([plottable_directions, 'b-'])
        plottable_lattice = route_spatial_lattice.get_plottable_lattice()
        config.PLOT_QUEUE.append([plottable_lattice, 'g.'])
    return route_spatial_lattice

def build_spatial_edges_sets(route_spatial_lattice):
    route_spatial_edges_sets = spatial_edges.SpatialEdgesSets(
                                            route_spatial_lattice)
    return route_spatial_edges_sets

def build_spatial_graphs_sets(route_spatial_edges_sets):
    """Build SpatialGraphsSets object from SpatialEdgesSets object
    """
    route_spatial_graphs_sets = spatial_graphs.SpatialGraphsSets(
                                        route_spatial_edges_sets)
    if config.VISUAL_MODE:
        pass
    return route_spatial_graphs_sets


def city_pair_to_spatial_graphs_sets(start, end):
    route_directions = build_directions(start, end)
    route_spatial_lattice = build_spatial_lattice(route_directions)
    route_spatial_edges_sets = build_spatial_edges_sets(route_spatial_lattice)
    route_spatial_graphs_sets = build_spatial_graphs_sets(
                                     route_spatial_edges_sets)
    return route_spatial_graphs_sets

