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
    directions = directions.get_directions(start, end)
    return directions

def build_spatial_lattice(directions):
    """Build lattice between directions points and spline points
    """
    spatial_lattice = lattice.SpatialLattice(directions_geospatials, 9, 7)
    if config.VISUAL_MODE:
        plottable_spline = spatial_lattice.get_plottable_spline()
        config.PLOT_QUEUE.append([plottable_spline, 'r-'])
        plottable_directions = spatial_lattice.get_plottable_directions()
        config.PLOT_QUEUE.append([plottable_directions, 'b-'])
        plottable_lattice = spatial_lattice.get_plottable_lattice()
        config.PLOT_QUEUE.append([plottable_lattice, 'g.'])
    return spatial_lattice

def build_spatial_edges_sets(spatial_lattice):
    spatial_edges_sets = edges.SpatialEdgesSets(spatial_lattice)
    return spatial_edges_sets

def build_spatial_graphs_sets(spatial_edges_sets):
    """Build SpatialGraphsSets object from SpatialEdgesSets object
    """
    spatial_graphs_sets = graphs.SpatialGraphsSets(spatial_edges_sets)
    if config.VISUAL_MODE:
        pass
    return spatial_graphs_sets

def city_pair_to_spatial_paths_3d_sets(start, end):
    directions = build_directions(start, end)
    spatial_lattice = build_spatial_lattice(directions)
    spatial_edges_sets = build_spaital_edges_sets(spatial_lattice)
    spatial_graphs_sets = build_spatial_graphs_sets(spatial_edges_sets)
    spatial_paths_2d_sets = build_spatial_paths_2d_sets(spatial_graphs_sets)
    spatial_paths_3d_sets = build_spatial_paths_3d_sets(spatial_paths_2d_sets)
    return spatial_paths_3d_sets
    

