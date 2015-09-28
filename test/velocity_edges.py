"""
Original Developer: Jonathan Ward
"""

import abstract_edges

class SpeedProfileEdge(abstract_edges.AbstractEdge):

    def __init__(self, start_speed_point, end_speed_point):
        abstract.AbstractEdge.__init__(start_speed_point, end_speed_point)


class VelocityProfileEdgesSets(abstract_edges.AbstractEdgesSets):

    def velocity_profile_edge_builder(self, start_velocity, end_velocity):
        velocity_profile_edge = VelocityProfileEdge(
            start_velocity, end_velocity)
        return velocity_profile_edge

    @staticmethod
    def is_velocity_profile_edge_pair_compatible(self, velocity_profile_edge_a,
                                                 velocity_profile_edge_b):
        return abstract.AbstractEdgesSets.is_edge_pair_compatible(
            velocity_profile_edge_a, velocity_profile_edge_b,
            self.velocity_profile_edge_degree_constraint)

    def __init__(self, velocities_lattice):
        abstract.AbstractEdgesSets.__init__(velocities_lattice,
