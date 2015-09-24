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
        self.pylons_costs = [pylon_cost.compute_pylon_cost(start_pylon),
                             pylon_cost.compute_pylon_cost(end_pylon)]

class TubeEdgesSets(abstract.AbstractEdgesSets):

    def __init__(self, pylons_lattice, tube_degree_constraint):
        abstract.AbstractEdgesSets.__init__(self, pylons_lattice,
                                            TubeEdge,
                                            tube_degree_constraint)

