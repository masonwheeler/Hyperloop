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
    slopes = np.divide(velocity_differences, time_differences)
    num_time_steps = int(trip_time / time_step_size)
    time_steps = np.empty(num_time_steps)
    time_steps.fill(time_step_size)
    cumulative_time_steps = np.cumsum(time_steps)
    selected_indices = np.searchsorted(times_by_arc_length,
                                       cumulative_time_steps)
    selected_times_by_arc_length = times_by_arc_length[selected_indices]
    selected_velocities_by_arc_length = velocities_by_arc_length[
                                                    selected_indices]
    selected_slopes = slopes[selected_indices]
    excess_times = np.subtract(cumulative_time_steps,
                               selected_times_by_arc_length)
    excess_velocities = np.multiply(excess_times, selected_slopes)
    velocities_by_time = np.add(excess_velocities, 
                                selected_velocities_by_arc_length)
    return [velocities_by_time, cumulative_time_steps]

def constrain_velocity_profile_longitudinal_accelerations(velocities_by_time,
                  time_step_size, max_longitudinal_acceleration):
    pass

