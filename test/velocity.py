"""
Original Developer: Jonathan Ward.

Purpose of Module: To provide a naive velocity profile generation method.

Last Modified: 8/16/15.

Last Modified By: Jonathan Ward.

Last Modification Purpose: Created Module.
"""

# Standard Modules
import numpy as np


def velocities_by_arc_length_to_times_by_arc_length(velocities_by_arc_length,
                                                                 arc_lengths):
    arc_length_intervals = np.ediff1d(arc_lengths)
    velocities_a = velocities_by_arc_length[:-1]
    velocities_b = velocities_by_arc_length[1:]
    velocities_sums = velocities_a + velocities_b
    mean_velocities = np.divide(velocities_sums, 2)
    interval_times = np.divide(arc_length_intervals,
                                    mean_velocities)
    cumulative_interval_times = np.cumsum(interval_times)
    times_by_arc_length = np.insert(cumulative_interval_times, 0, 0)
    return times_by_arc_length

def velocities_by_arc_length_to_velocities_by_time(velocities_by_arc_length,
                                                arc_lengths, time_step_size):
    times_by_arc_length = velocities_by_arc_length_to_times_by_arc_length(
                                        velocities_by_arc_length, arc_lengths)
    trip_time = times_by_arc_length[-1]
    time_differences = np.ediff1d(times_by_arc_lengths)
    velocity_differences = np.ediff1d(velocities_by_arc_length)
    num_time_steps = int(trip_time / time_step_size)
    time_steps = np.empty(num_time_steps)
    time_steps.fill(time_step_size)
    cumulative_time_steps = np.cumsum(time_steps)
    times_indices = np.searchsorted(times_by_arc_length, cumulative_time_steps)

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

