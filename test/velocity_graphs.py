"""
Original Developer: Jonathan Ward
"""

class VelocityProfileGraph(abstract.AbstractGraph):
    velocity_arc_length_step_size = config.VELOCITY_ARC_LENGTH_STEP_SIZE

    def reparametrize_velocities(self, velocities_by_arclength):
        velocities_by_time = reparametrize_velocities(velocities_by_arc_length,
                                                      velocity_arc_length_step_size)
        return velocities_by_time

    def compute_comfort(self, velocities_by_time):
        return comfort

    def compute_trip_time(self, velocities_by_time):
        return trip_time

    def __init__(self, start_id, end_id, start_angle, end_angle, num_edges,
                 velocities_by_arclength):
        abstract.AbstractGraph.__init__(start_id, end_id, start_angle, end_angle,
                                        num_edges)
        self.velocities_by_arc_length = velocities_by_arc_length
        velocities_by_time = self.reparametrize_velocity(
            velocities_by_in_arc_length)
        self.velocities_by_time = velocities_by_time
        self.comfort = self.compute_comfort(velocities_by_time)
        self.triptime = self.compute_trip_time(velocities_by_time)

    @classmethod
    def init_from_velocity_profile_edge(cls, velocity_profile_edge):
        start_id = velocity_profile_edge.start_id
        end_id = velocity_profile_edge.end_id
        start_angle = velocity_profile_edge.start_angle
        end_angle = velocity_profile_edge.end_angle
        num_edges = 1
        velocities_by_arc_length = [velocity_profile_edge.start_velocity,
                                    velocity_profile_edge.end_velocity]
        data = cls(StartId, end_id, start_angle, end_angle, num_edges,
                   velocities_by_arc_length)
        return data

    @classmethod
    def merge_two_velocity_profile_graphs(cls, velocity_profile_graph_a,
                                          velocity_profile_graph_b):
        start_id = velocity_profile_graph_a.start_id
        end_id = velocity_profile_graph_b.end_id
        start_angle = velocity_profile_graph_a.start_angle
        end_angle = velocity_profile_graph_b.end_angle
        num_edges = velocity_profile_graph_a.num_edges + \
            velocity_profile_graph_b.num_edges
        velocities_by_arc_length = velocity_profile_graph_a.velocities_by_arc_length + \
            velocity_profile_graph_b.velocities_by_arc_length
        data = cls(start_id, end_id, start_angle, end_angle, num_edges,
                   velocities_by_arc_length)
        return data

class VelocityProfileGraphsSet(abstract.AbstractGraphsSet):

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


