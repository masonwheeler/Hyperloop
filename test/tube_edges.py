"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import abstract_edges
import angle_constraint
import curvature
import parameters


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

    def compute_tunneling_cost(self, edge_length, tube_point_a, tube_point_b):
        if tube_point_a.is_underground and tube_point_b.is_underground:
            tunneling_cost = (edge_length *
                              parameters.TUNNELING_COST_PER_METER)
        if tube_point_a.is_underground and not tube_point_b.is_underground:
            tunneling_cost = (0.5 * edge_length *
                              parameters.TUNNELING_COST_PER_METER)
        if not tube_point_a.is_underground and tube_point_b.is_underground:
            tunneling_cost = (0.5 * edge_length *
                              parameters.TUNNELING_COST_PER_METER)
        if not tube_point_a.is_underground and not tube_point_b.is_underground:
            tunneling_cost = 0.0
        return tunneling_cost

    def compute_tube_cost(self, edge_length):
        tube_cost = edge_length * parameters.TUBE_COST_PER_METER
        return tube_cost

    def compute_edge_length(self, tube_point_a, tube_point_b):
        tube_coords_a = [tube_point_a.geospatial[0], tube_point_b.geospatial[1],
                         tube_point_a.tube_elevation]
        tube_coords_b = [tube_point_b.geospatial[0], tube_point_b.geospatial[1],
                         tube_point_b.tube_elevation]
        edge_vector = util.subtract(tube_coords_a, tube_coords_b)
        edge_length = np.linalg.norm(edge_vector)
        return edge_length

    def __init__(self, tube_point_a, tube_point_b):
        abstract.AbstractEdge.__init__(self, tube_point_a, tube_point_b)
        edge_length = self.compute_edge_length(tube_point_a, tube_point_b)
        self.tube_cost = self.compute_tube_cost(edge_length)
        self.tunneling_cost = self.compute_tunneling_cost(edge_length)
        self.pylons_costs = [tube_point_a.pylon_cost, tube_point_b.pylon_cost]


class TubeEdgesSets(abstract_edges.AbstractEdgesSets):

    def __init__(self, tube_points_lattice, tube_degree_constraint):
        abstract_edges.AbstractEdgesSets.__init__(self, tube_points_lattice,
                                                                   TubeEdge,
                                                     tube_degree_constraint)

