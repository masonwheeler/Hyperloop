"""
Original Developer: Jonathan Ward.

Purpose of Module: To provide a method for reparametrizing velocities

Last Modified: 8/16/15.

Last Modified By: Jonathan Ward.

Last Modification Purpose: Created Module.
"""

# Standard Modules:
import math
import numpy as np
import scipy.signal

# Custom Modules:
import parameters


def constrain_longitudinal_acceleration(speeds_by_arc_length, arc_lengths):
    max_longitudinal_acceleration = parameters.MAX_LONGITUDINAL_ACCEL
    rel_min_speeds_indices_tuple = scipy.signal.argrelmin(speeds_by_arc_length,
                                                                      order=5)
    rel_min_speeds_indices = rel_min_speeds_indices_tuple[0].tolist()
    arc_length_step_size = arc_lengths[1]
    for rel_min_speed_index in rel_min_speeds_indices:
        rel_min_speed = speeds_by_arc_length[rel_min_speed_index]
        squared_rel_min_speed = rel_min_speed**2
        relevant_arc_length_span = ((parameters.MAX_SPEED**2 -rel_min_speed**2)/
                                            (2 * max_longitudinal_acceleration))
        relevant_arc_length_indices_span = int(relevant_arc_length_span/
                                                   arc_length_step_size)
        min_relevant_index = max(0, rel_min_speed_index -
                                    relevant_arc_length_indices_span)
        max_relevant_index = min(len(speeds_by_arc_length),
            rel_min_speed_index + relevant_arc_length_indices_span)
        min_relative_index = min_relevant_index - rel_min_speed_index
        max_relative_index = max_relevant_index - rel_min_speed_index
        relative_indices_range = range(min_relative_index, max_relative_index)
        relative_indices_array = np.array(relative_indices_range)
        absolute_relative_indices_array = np.absolute(relative_indices_array)
        relative_distances_array = (absolute_relative_indices_array *
                                                arc_length_step_size)
        max_squared_speed_changes = (relative_distances_array * 2 *
                                     max_longitudinal_acceleration)
        max_squared_speeds = max_squared_speed_changes + squared_rel_min_speed
        max_speeds = np.sqrt(max_squared_speeds)
        speeds_by_arc_length[min_relevant_index : max_relevant_index] = \
            np.minimum(speeds_by_arc_length[min_relevant_index :
                                            max_relevant_index],
                       max_speeds)
    return speeds_by_arc_length        

def speeds_by_arc_length_to_times_by_arc_length(speeds_by_arc_length,
                                                         arc_lengths):
    arc_length_intervals = np.ediff1d(arc_lengths)
    speeds_a = speeds_by_arc_length[:-1]
    speeds_b = speeds_by_arc_length[1:]
    speeds_sums = speeds_a + speeds_b
    mean_speeds = np.divide(speeds_sums, 2)
    interval_times = np.divide(arc_length_intervals, mean_speeds)   
    cumulative_interval_times = np.cumsum(interval_times)
    times_by_arc_length = np.insert(cumulative_interval_times, 0, 0)
    return times_by_arc_length

def speeds_by_arc_length_to_speeds_by_time(speeds_by_arc_length,
                                    arc_lengths, time_step_size):
    times_by_arc_length = speeds_by_arc_length_to_times_by_arc_length(
                                        speeds_by_arc_length, arc_lengths)
    trip_time = times_by_arc_length[-1]
    time_differences = np.ediff1d(times_by_arc_length)
    speed_differences = np.ediff1d(speeds_by_arc_length)
    slopes = np.divide(speed_differences, time_differences)
    num_time_steps = int(trip_time / time_step_size)
    time_steps = np.empty(num_time_steps)
    time_steps.fill(time_step_size)
    cumulative_time_steps = np.cumsum(time_steps)
    cumulative_time_steps = np.append(cumulative_time_steps, trip_time)
    selected_indices = np.searchsorted(times_by_arc_length,
                                       cumulative_time_steps)
    selected_times_by_arc_length = times_by_arc_length[selected_indices]
    selected_speeds_by_arc_length = speeds_by_arc_length[
                                                    selected_indices]
    selected_slopes = slopes[selected_indices - 1]
    excess_times = np.subtract(cumulative_time_steps,
                               selected_times_by_arc_length)
    excess_speeds = np.multiply(excess_times, selected_slopes)
    speeds_by_time = np.add(excess_speeds, 
                                selected_speeds_by_arc_length)
    return [speeds_by_time, cumulative_time_steps]

def constrain_and_reparametrize_speeds(speeds_by_arc_length, arc_lengths,
                                                          time_step_size):
    constrained_speeds_by_arc_length = constrain_longitudinal_acceleration(
                                         speeds_by_arc_length, arc_lengths)
    speeds_by_time, cumulative_time_steps = \
        speeds_by_arc_length_to_speeds_by_time(constrained_speeds_by_arc_length,
                                                    arc_lengths, time_step_size)
    time_elapsed = cumulative_time_steps[-1]
    return [speeds_by_time, time_elapsed]
