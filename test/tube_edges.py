"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import abstract_edges
import angle_constraint
import curvature
import parameters
import pylon_cost
import tube_cost

def compute_tube_degree_constraint(pylon_arc_length_spacing,
                                     pylon_height_step_size,
                                          tube_interpolator):
    length_scale = pylon_arc_length_spacing
    resolution = pylon_height_step_size
    max_curvature = curvature.compute_curvature_threshold(parameters.MAX_SPEED,
                                                 parameters.MAX_VERTICAL_ACCEL)
    degree_constraint = angle_constraint.compute_angle_constraint(
           length_scale, tube_interpolator, max_curvature, resolution)
    return degree_constraint       

class TubeEdge(abstract_edges.AbstractEdge):

    def __init__(self, start_pylon, end_pylon):
        abstract.AbstractEdge.__init__(self, start_pylon, end_pylon)
        self.tube_coords = [start_pylon.tube_coords, end_pylon.tube_coords]
        self.tube_cost = tube_cost.compute_pylon_cost(self.tube_coords)
        self.pylon_cost = self.pylon_cost(start_pylon, end_pylon)


class TubeEdgesSets(abstract.AbstractEdgesSets):

    def tube_edge_builder(self, start_pylon, end_pylon):
        tube_edge = TubeEdge(start_pylon, end_pylon)
        return tube_edge

    @staticmethod
    def is_tube_edge_pair_compatible(tube_edge_a, tube_edge_b):
        edge_pair_compatible = abstract.AbstractEdgesSets.is_edge_pair_compatible(
            tube_edge_a, tube_edge_b, config.TUBE_DEGREE_CONSTRAINT)
        return edge_pair_compatible

    def __init__(self, pylons_lattice):
        abstract.AbstractEdgesSets.__init__(self, pylons_lattice,
                                            self.tube_edge_builder,
                                            self.is_tube_edge_pair_compatible)

