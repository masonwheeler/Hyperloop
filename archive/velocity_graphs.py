"""
Original Developer: Jonathan Ward
"""

import abstract_graphs
import reparametrize_speeds
import pod_orientation

class SpeedProfileGraph(abstract_graphs.AbstractGraph):

    def determine_pod_orientation(self):

    def compute_comfort_rating_and_trip_time(self):

    def __init__(self, abstract_graph, speeds_by_arc_length, arc_lengths)
        abstract.AbstractGraph.__init__(self,
                                        abstract_graph.start_id, 
                                        abstract_graph.end_id,
                                        abstract_graph.start_angle,
                                        abstract_graph.end_angle
                                        abstract_graph.abstract_coords)
        self.speeds_by_arc_length = speeds_by_arc_length
        self.arc_lengths = arc_lengths

    @classmethod
    def init_from_speed_profile_edge(cls, speed_profile_edge):
        abstract_edge = speed_profile_edge.to_abstract_edge()
        abstract_graph = abstract_graphs.AbstractGraph.init__from_abstract_edge(
                                                                  abstract_edge)
        speeds_by_arc_length = speed_profile_edge.speeds_by_arc_length
        arc_lengths = speed_profile_edge.arc_lengths
        data = cls(abstract_graph, speeds_by_arc_lengths, arc_lengths)
        return data

    @classmethod
    def merge_two_speed_profile_graphs(cls, speed_profile_graph_a,
            speed_profile_graph_b, graph_interpolator, resolution):
        abstract_graph_a = speed_profile_graph_a.to_abstract_graph()
        abstract_graph_b = speed_profile_graph_b.to_abstract_graph()
        merged_abstract_graph = \
          abstract_graphs.AbstractGraph.merge_abstract_graphs(abstract_graph_a,
                                                              abstract_graph_b)
        speeds_by_arc_length = (speed_profile_graph_a.speeds_by_arc_length +
                                speed_profile_graph_b.speeds_by_arc_length)
        arc_lengths = (speed_profile_graph_a.arc_lengths +
                       speed_profile_graph_b.arc_lengths)
        data = cls(merged_abstract_graph, speeds_by_arc_length, arc_lengths)
        return data

    def to_abstract_graph(self):
        abstract_graph = abstract_graphs.AbstractGraph(self.start_id,
                                                       self.end_id,
                                                       self.start_angle,
                                                       self.end_angle,
                                                       self.abstract_coords)
        return abstract_graph


class SpeedProfileGraphsSet(abstract_graphs.AbstractGraphsSet):
    NUM_FRONTS_TO_SELECT = 3

    def fetch_speed_profile_graphs_comforts_and_trip_times(self,
                                           speed_profile_graphs):
        speed_profile_graphs_
        

    def velocity_profile_graphs_comfort_triptime(self, velocity_profile_graphs):
        graphs_comfort_and_trip_time = [[graph.comfort, graph.triptime] for graph
                                        in velocity_profile_graphs]
        return graphs_comfort_and_trip_time

    def __init__(self, velocity_profile_graphs):
        minimize_comfort = False
        minimize_trip_time = True
        abstract.AbstractGraphSets.__init__(velocity_profile_graphs,
                                            self.                                       velocity_profile_graphs_comfort_triptime,
                                            minimize_comfort, minimize_trip_time)

    @classmethod
    def init_from_velocity_profile_edges_sets(cls, velocity_profile_edges_sets):
        velocity_profile_graphs = [
            map(VelocityProfileGraph.init_from_velocity_profile_edge,
                velocity_profile_edges_set)
            for velocity_profile_edges_set in velocity_profile_edges_sets]
        return cls(velocity_profile_graphs)


