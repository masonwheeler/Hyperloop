"""
Original Developer: Jonathan Ward.

Purpose of Module: To provide a method for computing time.

Last Modified: 9/5/2015.

Last Modified By: Jonathan Ward.

Last Modification Purpose: Created Modules.
"""

# Standard Modules:
import numpy as np

# Custom Modules:
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

