"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import numpy as np

# Custom Modules:
import parameters

def curvature_array_to_max_allowed_speeds(curvature_array, accel_constraint):
    curvature_array_length = curvature_array.size
    accel_constraint_array = np.empty(curvature_array_length)
    accel_constraint_array.fill(accel_constraint)
    max_allowed_speeds = np.sqrt(
        np.divide(accel_constraint_array,
                  curvature_array)
    )
    return max_allowed_speeds

def curvature_array_to_bounded_max_allowed_speeds(curvature_array,
                            accel_constraint, max_possible_speed):
    curvature_array_length = curvature_array.size
    max_possible_speeds = np.empty(curvature_array_length)
    max_possible_speeds.fill(max_possible_speed)
    max_allowed_speeds = curvature_array_to_max_allowed_speeds(curvature_array,
                                                          accel_constraint)
    bounded_max_allowed_speeds = np.minimum(max_allowed_speeds, max_possible_speeds)
    return bounded_max_allowed_speeds

def get_vertical_curvature_constrained_speeds(vertical_curvature_array):
    max_allowed_speeds = curvature_array_to_bounded_max_allowed_speeds(
            vertical_curvature_array, parameters.MAX_VERTICAL_ACCEL,
                                      parameters.MAX_SPEED)
    return max_allowed_speeds

def get_lateral_curvature_constrained_speeds(lateral_curvature_array):
    max_allowed_speeds = curvature_array_to_bounded_max_allowed_speeds(
        lateral_curvature_array, parameters.MAX_LATERAL_ACCEL,
                                 parameters.MAX_SPEED)
    return max_allowed_speeds

