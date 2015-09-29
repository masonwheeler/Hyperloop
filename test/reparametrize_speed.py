"""
Original Developer: Jonathan Ward.

Purpose of Module: To provide a method for reparametrizing velocities

Last Modified: 8/16/15.

Last Modified By: Jonathan Ward.

Last Modification Purpose: Created Module.
"""

# Standard Modules
import numpy as np
import scipy.signal

def constrain_longitudinal_acceleration_for_speeds_by_arc_length(
    speeds_by_arc_length, arc_lengths, max_longitudinal_acceleration,
                                                           max_speed):
    rel_min_speeds_indices = scipy.signal.argrelmin(speeds_by_arc_length)
    rel_min_speeds = speeds_by_arc_length[rel_min_speeds_indices]
    
    #num_speeds = speeds_by_arc_length.size
    #arc_length_intervals = np.ediff1d(arc_lengths)
    """
    for i in xrange(num_speeds - 1):            
        speed_a = speeds_by_arc_length[i]
        speed_b = speeds_by_arc_length[i + 1]
        arc_length_interval = arc_length_intervals[i]
        max_allowed_speed_b = np.sqrt(speed_a**2 + 
            2 * (max_longitudinal_acceleration * arc_length_interval))
        forward_constraint_satisfied = (speed_b < max_allowed_speed_b)
        if not forward_constraint_satisfied:
            speeds_by_arc_length[i + 1] = max_allowed_speed_b
    for i in reversed(xrange(num_speeds - 1)):
        speed_b = speeds_by_arc_length[i + 1]
        speed_a = speeds_by_arc_length[i]
        arc_length_interval = arc_length_intervals[i]
        max_allowed_speed_a = np.sqrt(speed_b**2 +
            2 * (max_longitudinal_acceleration * arc_length_interval))
        backward_constraint_satisfied = (speed_a <
                                         max_allowed_speed_a)
        if not backward_constraint_satisfied:
            speeds_by_arc_length[i] = max_allowed_speed_a
    """
    constrained_speeds_by_arc_length = 
    for i in range(speeds_by_arc_length.size):
      
    return speeds_by_arc_length        

def speeds_by_arc_length_to_times_by_arc_length(speeds_by_arc_length,
                                                         arc_lengths):
    arc_length_intervals = np.ediff1d(arc_lengths)
    speeds_a = speeds_by_arc_length[:-1]
    speeds_b = speeds_by_arc_length[1:]
    speeds_sums = speeds_a + speeds_b
    mean_speeds = np.divide(speeds_sums, 2)
    interval_times = np.divide(arc_length_intervals,
                                    mean_speeds)
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

def constrain_and_reparametrize_speeds_by_arc_length(speeds_by_arc_length,
               arc_lengths, time_step_size, max_longitudinal_acceleration):
    constrained_speeds_by_arc_length = \
        constrain_longitudinal_acceleration_for_speeds_by_arc_length(
            speeds_by_arc_length, arc_lengths, max_longitudinal_acceleration)
    raise ValueError
    speeds_by_time, cumulative_time_steps = \
        speeds_by_arc_length_to_speeds_by_time(speeds_by_arc_length,
                                        arc_lengths, time_step_size)
    time_elapsed = cumulative_time_steps[-1]
    return [speeds_by_time, time_elapsed]
