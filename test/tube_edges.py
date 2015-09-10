"""
Original Developer: Jonathan Ward
"""

class TubeEdge(abstract.AbstractEdge):

    def tube_cost(self, start_pylon, end_pylon):
        start_tube_coords = start_pylon.tube_coords
        end_tube_coords = end_pylon.tube_coords
        tube_vector = util.edge_to_vector([start_tube_coords, end_tube_coords])
        tube_length = util.norm(tube_vector)
        tube_cost = tube_length * config.TUBE_COST_PER_METER
        return tube_cost

    def pylon_cost(self, start_pylon, end_pylon):
        total_pylon_cost = start_pylon.pylon_cost + end_pylon.pylon_cost
        return total_pylon_cost

    def __init__(self, start_pylon, end_pylon):
        abstract.AbstractEdge.__init__(self, start_pylon, end_pylon)
        self.tube_coords = [start_pylon.tube_coords, end_pylon.tube_coords]
        self.tube_cost = self.tube_cost(start_pylon, end_pylon)
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

