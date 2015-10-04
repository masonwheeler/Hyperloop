"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import abstract_graphs
import curvature
import mergetree
import parameters
import reparametrize_speed


class TubeGraph(abstract_graphs.AbstractGraph):

    def compute_min_time_and_total_tube_cost(self, tube_curvature_array,
                                                            arc_lengths):
        max_allowed_speeds = \
            curvature.vertical_curvature_array_to_max_allowed_speeds(
                                                    tube_curvature_array)
        time_step_size = 1 #Second
        speeds_by_time, time_elapsed = \
            reparametrize_speed.constrain_and_reparametrize_speeds(
                   max_allowed_speeds, arc_lengths, time_step_size,
                                 parameters.MAX_LONGITUDINAL_ACCEL)
        self.min_time = time_elapsed
        self.total_cost = (self.pylon_cost + self.tube_cost
                                      + self.tunneling_cost)

    def fetch_min_time_and_total_cost(self):
        if self.min_time == None or self.total_cost == None:
            return None
        else: 
            min_time = round(self.min_time / 60.0, 3)
            total_cost = round(self.total_cost / 10.0**9, 3)
        return [min_time, total_cost]

    def __init__(self, abstract_graph
                 tube_cost, pylon_cost, tube_coords):
        abstract.AbstractGraph.__init__(self, start_id, end_id,
                                        start_angle, end_angle, num_edges)
        self.tube_cost = tube_cost
        self.pylon_cost = pylon_cost
        self.tube_coords = tube_coords
        self.triptime_excess = self.compute_triptime_excess(
            tube_coords, num_edges)

    @classmethod
    def init_from_tube_edge(cls, tube_edge):
        abstract_edge = tube_edge.to_abstract_edge()
        abstract_graph = abstract_graphs.AbstractGraph.init_from_abstract_edge(
                                                                 abstract_edge)
        pylon_cost = tube_edge.pylon_cost
        tube_cost = tube_edge.tube_cost
        tunneling_cost = tube_edge.tunneling_cost
        tube_coords = tube_edge.tube_coords
        data = cls(abstract_graph, pylon_cost, tube_cost, tunneling_cost,
                   tube_coords)
        return data

    @staticmethod
    def merge_tube_curvature_arrays(tube_graph_a

    @classmethod
    def merge_two_tube_graphs(cls, tube_graph_a, tube_graph_b):
        abstract_graph_a = spatial_graph_a.to_abstract_graph()
        abstract_graph_b = spatial_graph_b.to_abstract_graph()
        merged_abstract_graph = \
            abstract_graphs.AbstractGraph.merge_abstract_graphs(
                                 abstract_graph_a, abstract_graph_b)
        pylon_cost = tube_graph_a.pylon_cost + tube_graph_b.pylon_cost
        tube_cost = tube_graph_a.tube_cost + tube_graph_b.tube_cost
        tunneling_cost = (tube_graph_a.tunneling_cost +
                          tube_graph_b.tunneling_cost)
        tube_coords = util.smart_concat(tube_graph_a.tube_coords,
                                        tube_graph_b.tube_coords)
        data = cls(merged_abstract_graph, pylon_cost, tube_cost, tunneling_cost,
                   tube_coords)
        return data

    def to_abstract_graph(self):
        abstract_graph = abstract_graphs.AbstractGraph(self.start_id,
                                                       self.end_id,
                                                       self.start_angle,
                                                       self.end_angle,
                                                       self.abstract_coords)
        return abstract_graph


class TubeGraphsSet(abstract_graphs.AbstractGraphsSet):

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
                                            minimize_triptime_excess)

    @classmethod
    def init_from_tube_edges_set(cls, tube_edges_set):
        tube_graphs = map(TubeGraph.init_from_tube_edge, tube_edges_set)
        graphs_num_edges = 1
        return cls(tube_graphs, graphs_num_edges)


class TubeGraphsSets(abstract_graphs.AbstractGraphsSets):

    def tube_graph_interpolator(self, waypoint_tube_elevations,
                                 waypoint_tube_arc_lengths):
        interpolated_tube_elevations, tube_curvature_array = \
            self.tube_interpolator(waypoint_tube_elevations,
                                   waypoint_tube_arc_lengths)
        return [interpolated_tube_elevations, tube_curvature_array]

    def merge_two_tube_graphs(self, tube_graph_a, tube_graph_b):
        merged_tube_graph = TubeGraph.merge_two_tube_graphs(
            tube_graph_a, tube_graph_b, self.tube_graph_interpolator,
                                 self.tube_elevation_resolution)
        return merged_tube_graph

    def __init__(self, tube_edges_sets, tube_interpolator):
        self.tube_interpolator = tube_interpolator
