"""
Original Developer: Jonathan Ward
ies_purpose of Module: To provide a naive velocity profile generation method
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Created Module
"""

# Standard Modules
import numpy as np

# Our Modules
import abstract
import comfort
import config
import interpolate


def velocities_to_velocity_pairs(velocities):
    velocity_pairs = util.to_pairs(velocities)
    return velocity_pairs


def time_elapsed_to_velocity(velocity_pair, time_elapsed):
    start_velocity, end_velocity = velocity_pair
    start_velocity_time, start_velocity_val = start_velocity
    end_velocity_time, end_velocity_val = end_velocity
    velocity_difference = end_velocity_val - start_velocity_val
    time_difference = end_velocity_time - start_velocity_time
    relative_velocity_val = time_elapsed * velocity_difference / time_difference
    velocity_val = start_velocity_val + relative_velocity_val
    velocity_time = start_velocity_time + time_elapsed
    velocity = [velocity_time, velocity_val]
    return velocity


def sample_velocity_pair(velocity_pair, time_step_size, time_elapsed):
    sampled_velocities = []
    start_velocity, end_velocity = velocity_pair
    start_velocity_time, start_velocity_val = start_velocity
    end_velocity_time, end_velocity_val = end_velocity
    velocity_pairtime_difference = end_velocity_time - start_velocity_time
    while time_elapsed <= velocity_pair_time_difference:
        velocity = time_elapsed_to_velocity(velocity_pair, time_elapsed)
        sampled_velocities.append(velocity)
        time_elapsed += time_step_size
    time_elapsed -= velocity_pair_time_difference
    return [sampled_velocities, time_elapsed]


def sample_velocities(velocities_by_time, time_step_size):
    time_elapsed = 0
    velocities = []
    for velocity_pair in velocity_pairs:
        sampled_velocities, time_elapsed = sample_velocity_pair(velocity_pair,
                                                                time_elapsed)
        velocities += sampled_velocities
    return velocities


def velocities_by_arclength_to_time_checkpoints_array(velocities_by_arc_length,
                                                      velocity_arc_length_step_size):
    num_intervals = velocities_by_arc_length.size - 1
    velocity_arc_length_step_size_array = np.empty(num_intervals)
    velocity_arc_length_step_size_array.fill(velocity_arc_length_step_size)
    padded_velocities = np.append(velocities_by_arc_length, 0.0)
    shifted_velocities = np.insert(velocities_by_arc_length, 0, 0.0)
    padded_velocities_sums = np.add(padded_velocities, shifted_velocities)
    velocities_sums = padded_velocities_sums[1:-1]
    mean_velocities_by_arc_length = np.divide(velocities_sums, 2)
    times = np.divide(velocity_arc_length_step_size_array,
                      mean_velocities_by_arc_length)
    time_check_points_array = np.insert(times, 0, 0)
    return time_check_points_array


def compute_trip_time(velocities_by_arc_length, velocity_arc_length_step_size):
    time_checkpoints_array = velocities_by_arclength_to_time_checkpoints_array(
        velocities_by_arc_length, velocity_arc_length_step_size)
    trip_time = np.sum(time_checkpoints_array)
    return trip_time


def reparametrize_velocities(velocities_by_arc_length, velocity_arclength_step_size,
                             time_step_size):
    time_checkpoints_array = velocities_by_arclength_to_time_checkpoints_array(
        velocities_by_arc_length, velocity_arclength_step_size)
    times_elapsed = np.cumsum(time_checkpoints_array)
    velocities_by_time = np.array([times_elapsed, velocities_by_arc_length]).T
    sampled_velocities_by_time = sample_velocities(velocities_by_time)
    return sampled_velocities_by_time


def compute_local_trip_time_excess(max_allowed_velocities,
                                   velocity_arc_length_step_size):
    num_velocities = max_allowed_velocities.size
    max_possible_velocities = np.empty(num_velocities)
    max_possible_velocities.fill(config.MAX_SPEED)
    minimum_possible_trip_time = compute_trip_time(max_possible_velocities,
                                                   velocity_arc_length_step_size)
    ##print("max allowed velocities: " + str(max_allowed_velocities))
    minimum_allowed_trip_time = compute_trip_time(max_allowed_velocities,
                                                  velocity_arc_length_step_size)
    local_trip_time_excess = minimum_allowed_trip_time - minimum_possible_trip_time
    return local_trip_time_excess


def compute_max_endpoint_velocities(max_linear_accel, max_possible_velocity,
                                    velocity_arclength_step_size):
    velocity = 0
    max_end_point_velocities = []
    while velocity < max_possible_velocity:
        max_end_point_velocites.append(velocity)
        velocity = np.sqrt(2 * velocity_arc_length_step_size * max_linear_accel
                           + np.square(current_velocity))
    return max_end_point_velocities


def global_max_allowed_velocities(local_max_allowed_velocities,
                                  max_end_point_velocities):
    endpoint_velocities_length = max_end_point_velocities.length
    max_start_velocities = max_end_point_velocities
    max_end_velocities = max_end_point_velocities[::-1]
    local_max_start_velocities = local_max_allowed_velocities[
        :endpoint_velocities_length]
    local_max_end_velocities = local_max_allowed_velocities[
        -endpoint_velocities_length:]
    effective_max_start_velocities = np.minimum(max_start_velocities,
                                                local_max_start_velocities)
    effective_max_end_velocities = np.minimum(max_end_velocities,
                                              local_max_end_velocities)
    global_max_allowed_velocities = local_max_allowed_velocities
    global_max_allowed_velocities[:endpoint_velocities_length] = \
        effective_max_start_velocities
    global_max_allowed_velocities[-endpoint_velocities_length:] = \
        effective_max_end_velocities
    return global_max_allowed_velocities


class Velocity(abstract.AbstractPoint):

    def __init__(self, speed, distance_along_path, velocity_id):
        velocity_coords = {"speed": speed,
                           "distance_along_path":  distance_along_path}
        abstract.AbstractPoint.__init__(velocity_coords, velocity_id)


class VelocitiesSlice(abstract.AbstractSlice):

    def velocities_builder(self, velocities_slice_bounds, lowest_velocity_id):
        max_speed = velocities_slice_bounds["max_speed"]
        min_speed = velocities_slice_bounds["min_speed"]
        speed_step_size = velocities_slice_bounds["speed_step_size"]
        speed_difference = max_speed - min_speed
        speed_options = util.build_grid2(speed_difference,
                                         speeds_step_size, minimum_speed)
        velocity_ids = [index + lowest_velocity_id for index
                        in range(len(speed_options))]
        velocity_options = [Velocity(speed_options[i], distance_along_path,
                                     velocity_ids[i]) for i in range(len(velocity_ids))]
        return velocity_options

    def __init__(self, velocities_slice_bounds, lowest_velocity_id):
        abstract.AbstractSlice.__init__(velocities_slice_bounds,
                                        lowest_velocity_id, self.velocities_builder)


class VelocitiesLattice(abstract.AbstractLattice):

    def max_allowed_velocities_to_velocity_slice_bounds(max_allowed_velocities):
        num_arc_length_steps = max_allowed_velocities.length - 1
        arc_length_steps_array = np.empty(num_arc_length_points)
        arc_length_steps_array = np.fill(config.ARCLENGTH_STEP_SIZE)
        partial_arc_length_array = np.cumsum(arc_length_steps_array)
        arc_length_array = np.insert(partial_arc_length_array, 0, 0)
        velocity_slices_bounds = []
        for i in range(len(max_allowed_velocities.length)):
            max_speed = max_allowed_velocities[i]
            min_speed = config.SPEED_STEP_SIZE
            speed_step_size = config.SPEED_STEP_SIZE
            distance_along_path = arc_length_array[i]
            velocity_slice_bounds = {"max_speed": max_speed,
                                     "min_speed": min_speed,
                                     "speed_step_size": speed_step_size}
            velocity_slices_bounds.append(velocity_slice_bounds)
        return velocity_slices_bounds

    def __init__(self, max_allowed_velocities):
        velocity_slices_bounds = max_allowed_velocities_to_velocity_slice_bounds(
            max_allowed_velocities)
        abstract.AbstractLattice.__init__(velocities_slices_bounds,
                                          VelocitiesSlice)


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
                                            self.is_velocity_profile_edge_pair_compataible)


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
                                            self.velocity_profile_graphs_comfort_triptime,
                                            minimize_comfort, minimize_trip_time)

    @classmethod
    def init_from_velocity_profile_edges_sets(cls, velocity_profile_edges_sets):
        velocity_profile_graphs = [
            map(VelocityProfileGraph.init_from_velocity_profile_edge,
                velocity_profile_edges_set)
            for velocity_profile_edges_set in velocity_profile_edges_sets]
        return cls(velocity_profile_graphs)


def max_allowed_velocities_to_velocity_profile_graphs(max_allowed_velocities):
    velocities_lattice = VelocitiesLattice(max_allowed_velocities)
    velocity_profile_edges_sets = VelocityProfileEdgesSets(velocities_lattice)
    velocity_profile_graphs_set = \
        VelocityProfileGraphsSet.init_from_velocity_profile_edges_sets(
            velocity_profile_edges_sets)
    velocity_profile_graphs_sets_tree = merge_tree.MasterTree(
        velocity_profile_graphs_set, abstract.graphs_sets_merger,
        abstract.graphs_sets_updater)
    root_velocity_profile_graphs_set = velocity_profile_graphs_sets_tree.root
    selected_velocity_profile_graphs = root_velocity_profile_graphs_set.selected_graphs
    return selected_velocity_profile_graphs
