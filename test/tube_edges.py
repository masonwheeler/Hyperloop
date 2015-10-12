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

    def build_tube_points(self, resolution):
        tube_end_points = zip(self.arc_lengths, self.tube_elevations)
        tube_points = sample_path.sample_path_points(tube_end_points,
                                                     resolution)
        return tube_points

    def __init__(self, tube_point_a, tube_point_b):
        abstract_edges.AbstractEdge.__init__(self, tube_point_a, tube_point_b)

    def constrain_grade(self, max_grade):
        self.is_useful = abs(self.angle) < max_grade

    def attach_costs(self):
        self.arc_lengths = [tube_point_a.arc_length, tube_point_b.arc_length]
        self.tube_elevations = [tube_point_a.tube_elevation,
                                tube_point_b.tube_elevation]
        edge_length = self.compute_edge_length(tube_point_a, tube_point_b)
        self.tube_cost = self.compute_tube_cost(edge_length)
        self.tunneling_cost = self.compute_tunneling_cost(edge_length,
                                               tube_point_a, tube_point_b)
        self.pylons_costs = [tube_point_a.pylon_cost, tube_point_b.pylon_cost]

    def sample_edge(self, resolution):
        tube_edge_end_points = [self.arc_lengths, self.tube_elevations]
        sampled_tube_points = sample_path.sample_path_points(
                              tube_edge_end_points, resolution)
        self.sampled_arc_lengths, self.sampled_tube_elevations = \
            np.tranpose(sampled_tube_points)

    def to_abstract_edge(self):
        abstract_edge = abstract_edges.AbstractEdge(self.start_point,
                                                      self.end_point)
        return abstract_edge


class TubeEdgesSets(abstract_edges.AbstractEdgesSets):

    def contrain_edges_grades(self, edges_sets, max_grade):
        for edges_set in edges_sets:
            for edge in edges_set:
                edge.constraint_grade(max_grade)

    def attach_edges_costs(self, edges_sets):
        for edges_set in edges_sets:
            for edge in edges_set:
                edges.attach_costs()

    def sample_edges(self, edges_sets, resolution):
        for edges_set in edges_sets:
            for edge in edges_set:
                edge.sample_edge(resolution)    

    def __init__(self, tube_points_lattice, tube_degree_constraint, max_grade):
        abstract_edges.AbstractEdgesSets.__init__(self, tube_points_lattice,
                                                                   TubeEdge,
                                                     tube_degree_constraint)
        self.constrain_edges_grades(self.raw_edges_sets, max_grade)
        self.filtered_edges_sets = self.iterative_filter(self.raw_edges_sets)
        self.attach_edges_costs(self.filtered_edges_sets)
        self.sample_edges(self.filtered_edges_sets, resolution)
