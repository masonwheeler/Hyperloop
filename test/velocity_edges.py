"""
Original Developer: Jonathan Ward
"""

class VelocityProfileEdge(abstract.AbstractEdge):

    def __init__(self, start_velocity, end_velocity):
        abstract.AbstractEdge.__init__(start_velocity, end_velocity)


class VelocityProfileEdgesSets(abstract.AbstractEdgesSets):
    velocity_profile_edge_degree_constraint = config.VELOCITY_PROFILE_DEGREE_CONSTRAINT

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
                                            self.velocity_profile_edge_builder,
                                            self.                                       is_velocity_profile_edge_pair_compataible)

