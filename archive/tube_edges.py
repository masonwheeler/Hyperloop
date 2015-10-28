"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import numpy as np

# Custom Modules:
import abstract_edges
import angle_constraint
import curvature
import parameters
import sample_path


class TubeEdge(abstract_edges.AbstractEdge):

    MAX_TUBE_GRADE = parameters.MAX_TUBE_GRADE

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
        edge_vector = np.subtract(tube_coords_a, tube_coords_b)
        edge_length = np.linalg.norm(edge_vector)
        return edge_length

    def __init__(self, tube_point_a, tube_point_b):
        abstract_edges.AbstractEdge.__init__(self, tube_point_a, tube_point_b)
        self.is_useful = abs(self.angle) < self.MAX_TUBE_GRADE

    def attach_costs(self):
        edge_length = self.compute_edge_length(self.start_point, self.end_point)
        self.tube_cost = self.compute_tube_cost(edge_length)
        self.tunneling_cost = self.compute_tunneling_cost(edge_length,
                                               self.start_point, self.end_point)
        self.pylons_costs = [self.start_point.pylon_cost, self.end_point.pylon_cost]

    def sample_edge_tube_points(self, resolution):
        arc_lengths = [self.start_point.arc_length,
                       self.end_point.arc_length]
        tube_elevations = [self.start_point.tube_elevation,
                           self.end_point.tube_elevation]
        tube_edge_end_points = zip(arc_lengths, tube_elevations)
        sampled_tube_points, _ = sample_path.sample_path_points(
                                         tube_edge_end_points, resolution)
        self.sampled_arc_lengths, self.sampled_tube_elevations = \
            np.transpose(sampled_tube_points)

    def to_abstract_edge(self):
        abstract_edge = abstract_edges.AbstractEdge(self.start_point,
                                                      self.end_point)
        return abstract_edge


class TubeEdgesSets(abstract_edges.AbstractEdgesSets):

    def attach_edges_costs(self, edges_sets):
        for edges_set in edges_sets:
            for edge in edges_set:
                edge.attach_costs()

    def sample_edges_tube_points(self, edges_sets, resolution):
        for edges_set in edges_sets:
            for edge in edges_set:
                edge.sample_edge_tube_points(resolution)

    def __init__(self, tube_points_lattice, tube_degree_constraint):
        self.arc_lengths = tube_points_lattice.arc_lengths
        self.land_elevations = tube_points_lattice.land_elevations
        self.lower_tube_envelope = tube_points_lattice.lower_tube_envelope
        self.upper_tube_envelope = tube_points_lattice.upper_tube_envelope
        abstract_edges.AbstractEdgesSets.__init__(self, tube_points_lattice,
                                               TubeEdge, tube_degree_constraint)
        resolution = tube_points_lattice.resolution
        self.filtered_edges_sets = self.iterative_filter(self.raw_edges_sets)
        self.attach_edges_costs(self.filtered_edges_sets)
        self.sample_edges_tube_points(self.filtered_edges_sets, resolution)
