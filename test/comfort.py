"""
Original Developer: David Roberts
Purpose of Module: To evaluate passenger comfort using
                   Sperling's comfort index (Wz).

Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify naming and add citations.

Citations:
   "Ride comfort in Tilting Trains"
    - Johan Forstberg
   "Experimental and Analytical Ride Comfort Evaluation of a Railway Coach"
    - K. V. Gangadharan

OUTLINE of SCRIPT (comfort.py):
input vars: {t_i}, {x_i}, {v_i}, {a_i} (four lists of points in 3_d space)
output vars: c (comfort rating)

SUB-SCRIPTS:
 1. Find acceleration in passenger frame:
      {t_i}, {v_i}, {a_i}  -->  {ap_i}
 2. Take Fast Fourier Transform of passenger accel:
      {ap_i}  -->  {ap_f}
 3. Apply weighting filter and sum results
      {ap_f} --> {w(f)*ap_f} --> c = sum_f |w(f)*ap_f|^2
"""

# Standard Modules:
import math
import numpy as np


def accel_passenger(vel, accel, component):
    """
    Find acceleration in passenger frame:
       {t_i}, {v_i}, {a_i}  -->  {T_i}, {N_i}, {B_i} -->  {ap_i}
    """
    tangent_vector = [vel[i] / np.linalg.norm(vel[i]) for i in range(len(vel))]
    normal_vector = [np.cross(vel[i], np.cross(accel[i], vel[i])) /
                     np.linalg.norm(
                         np.cross(vel[i], np.cross(accel[i], vel[i])))
                     for i in range(len(vel))]
    binormal_vector = [np.cross(tangent_vector[i], normal_vector[i])
                       for i in range(len(vel))]

    # Change of basis matrix for transforming to the tangent, normal, binormal
    # (passenger) frame.
    change_of_basis_matrix = [np.linalg.inv(np.matrix.transpose(
        np.array([tangent_vector[i], normal_vector[i], binormal_vector[i]])))
        for i in range(len(vel))]

    # Apply change of basis to write the acceleration in tangent, normal, binormal
    # (passenger) frame.
    accel_passenger = [np.dot(change_of_basis_matrix[i], accel[i])
                       for i in range(len(vel))]
    accel_passenger_components = [accel_passenger_val[component] for
                                  accel_passenger_val in accel_passenger]
    return accel_passenger_components

def vertical_weighting_factor(frequency):
    vertical_weighting_factor = 0.588 * math.sqrt(
        (1.911 * frequency**2 + (.25 * frequency**2)**2) /
        ((1 - 0.2777 * frequency**2)**2 +
            (1.563 * frequency - 0.0368 * frequency**3)**2))
    return vertical_weighting_factor

def horizontal_weighting_factor(frequency):
    return 1.25 * vertical_weighting_factor(frequency)

def weighting_factors(frequency):
    """
    See (Gangadharan) equations (7) and (8) for weighting factors.
    """
    weighting_factors = [0, vertical_weighting_factor(frequency),
                            horizontal_weighting_factor(frequency)]
    return weighting_factors

def frequency_weighted_rms(accel_frequency, time_interval, component):
    """
    See (Forstberg) equation (3.1) for Sperling Comfort Index equation.
    """
    frequency_width = float(len(accel_frequency))
    time_interval = float(time_interval)
    frequency_half_width = int(math.floor(frequency_width / 2.0))
    accel_frequency_weighted = [
        (weighting_factors(frequency_index / time_interval)[component]
         * accel_frequency[frequency_index]) for frequency_index
        in range(-frequency_half_width, frequency_half_width + 1)]
    frequency_weighted_r_m_s = np.sqrt(sum([np.absolute(accel_val)**2
                                            for accel_val in accel_frequency_weighted]))
    return frequency_weighted_r_m_s

def sperling_comfort_index(vel, accel, time_interval, component):
    """
    2. Take Fast Fourier Transform of psnger accel:
          {ap_i}  -->  {ap_f}
    3. Apply weighting filter and sum results
          {ap_f} --> {w(f)*ap_f} --> c = sum_f |w(f)|^2
    """
    num_time_points = len(vel)
    accel_passenger_components = accel_passenger(vel, accel, component)
    accel_passenger_frequency = np.fft.fft(
        accel_passenger_components) / num_time_points
    accel_frequency_weighted_r_m_s = frequency_weighted_rms(accel_passenger_frequency,
                                                            time_interval, component)
    sperling_comfort_index = 4.42 * (accel_frequency_weighted_r_m_s)**0.3
    return sperling_comfort_index


