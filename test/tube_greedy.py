"""
Original Developer: Jonathan Ward
"""

import tube_lattice
import tube_edges
import tube_graphs


def elevation_profile_to_tube_graphs(elevation_profile):
    tube_lattice = tube_lattice.TubeLattice(elevation_profile)
    tube_edges_sets = tube_edges.TubeEdgesSets(tube_lattice)
    tube_graphs_sets = tube_graphs.TubeGraphsSets(tube_edges_sets)
    selected_tube_graphs = tube_graphs_sets.selected_graphs
    return selected_tube_graphs
