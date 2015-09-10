"""
Original Developer: Jonathan Ward
"""

class TubeGraph(abstract.AbstractGraph):

    velocity_arc_length_step_size = config.VELOCITY_ARC_LENGTH_STEP_SIZE

    def compute_triptime_excess(self, tube_coords, num_edges):
        if num_edges < config.TUBE_TRIP_TIME_EXCESS_MIN_NUM_EDGES:
            return None
        else:
            z_values = [tube_coord[2] for tube_coord in tube_coords]
            local_max_allowed_vels = interpolate.points_1d_local_max_allowed_vels(
                z_values)
            triptime_excess = velocity.compute_local_trip_time_excess(
                local_max_allowed_vels, self.velocity_arc_length_step_size)
            return triptime_excess

    def __init__(self, start_id, end_id, start_angle, end_angle, num_edges,
                 tube_cost, pylon_cost, tube_coords):
        abstract.AbstractGraph.__init__(self, start_id, end_id,
                                        start_angle, end_angle, num_edges)
        self.tube_cost = tube_cost
        self.pylon_cost = pylon_cost
        self.tube_coords = tube_coords
        self.triptime_excess = self.compute_triptime_excess(
            tube_coords, num_edges)

    def tube_cost_trip_time_excess(self):
        cost_trip_time_excess = [self.tube_cost + self.pylon_cost,
                                 self.triptime_excess]
        #print("tube cost: " + str(self.tube_cost))
        #print("pylon cost: " + str(self.pylon_cost))
        #print("trip time excess: " + str(self.triptime_excess))
        return cost_trip_time_excess

    @classmethod
    def init_from_tube_edge(cls, tube_edge):
        start_id = tube_edge.start_id
        end_id = tube_edge.end_id
        start_angle = tube_edge.angle
        end_angle = tube_edge.angle
        num_edges = 1
        tube_cost = tube_edge.tube_cost
        pylon_cost = tube_edge.pylon_cost
        tube_coords = tube_edge.tube_coords
        data = cls(start_id, end_id, start_angle, end_angle, num_edges, tube_cost,
                   pylon_cost, tube_coords)
        return data

    @classmethod
    def merge_two_tube_graphs(cls, tube_graph_a, tube_graph_b):
        start_id = tube_graph_a.start_id
        end_id = tube_graph_b.end_id
        start_angle = tube_graph_a.start_angle
        end_angle = tube_graph_b.end_angle
        num_edges = tube_graph_a.num_edges + tube_graph_b.num_edges
        tube_cost = tube_graph_a.tube_cost + tube_graph_b.tube_cost
        pylon_cost = tube_graph_a.pylon_cost + tube_graph_b.pylon_cost
        tube_coords = util.smart_concat(tube_graph_a.tube_coords,
                                        tube_graph_b.tube_coords)
        data = cls(start_id, end_id, start_angle, end_angle, num_edges, tube_cost,
                   pylon_cost, tube_coords)
        return data


class TubeGraphsSet(abstract.AbstractGraphsSet):

    @staticmethod
    def is_graph_pair_compatible(graph_a, graph_b):
        graphs_compatible = abstract.AbstractGraphsSet.is_graph_pair_compatible(
            graph_a, graph_b, config.TUBE_DEGREE_CONSTRAINT)
        return graphs_compatible

    @staticmethod
    def tubegraphs_cost_triptime_excess(tube_graphs, graphs_num_edges):
        if graphs_num_edges < config.TUBE_TRIP_TIME_EXCESS_MIN_NUM_EDGES:
            return None
        else:
            graphs_cost_triptime_excess = [tube_graph.tube_cost_trip_time_excess()
                                           for tube_graph in tube_graphs]
            return graphs_cost_triptime_excess

    def __init__(self, tube_graphs, graphs_num_edges):
        minimize_cost = True
        minimize_triptime_excess = True
        abstract.AbstractGraphsSet.__init__(self, tube_graphs,
                                            self.tubegraphs_cost_triptime_excess,
                                            self.is_graph_pair_compatible,
                                            minimize_cost,
                                            minimize_triptime_excess,
                                            graphs_num_edges)

    @classmethod
    def init_from_tube_edges_set(cls, tube_edges_set):
        tube_graphs = map(TubeGraph.init_from_tube_edge, tube_edges_set)
        graphs_num_edges = 1
        return cls(tube_graphs, graphs_num_edges)

