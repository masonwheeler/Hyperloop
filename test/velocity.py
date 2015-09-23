"""
Original Developer: Jonathan Ward.

Purpose of Module: To provide a naive velocity profile generation method.

Last Modified: 8/16/15.

Last Modified By: Jonathan Ward.

Last Modification Purpose: Created Module.
"""

# Standard Modules
import numpy as np
import time

# Our Modules
import config

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


def velocities_by_arc_length_to_time_checkpoints(velocities_by_arc_length,
                                                             arc_lengths):
    arc_length_intervals = np.ediff1d(arc_lengths)
    velocities_a = velocities_by_arc_length[:-1]
    velocities_b = velocities_by_arc_length[1:]
    velocities_sums = velocities_a + velocities_b
    mean_velocities = np.divide(velocities_sums, 2)
    ##print "arc lengths size: " + str(arc_length_intervals.size)
    ##print "mean velocities size: " + str(mean_velocities.size)
    interval_times = np.divide(arc_length_intervals,
                                    mean_velocities)
    interval_end_time_checkpoints = np.cumsum(interval_times)
    time_checkpoints = np.insert(interval_end_time_checkpoints, 0, 0)
    return time_checkpoints

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

