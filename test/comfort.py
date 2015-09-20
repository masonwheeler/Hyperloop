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

class ComfortProfile(object):

    LP_NORM_POWER = 10

    def compute_spatial_component_derivative(self, spatial_component_coords):
        spatial_component_derivative = util.numerical_derivative(
                        spatial_component_coords, self.time_checkpoints)
        return spatial_component_derivative

    def compute_velocities_components(self):
        x_component_coords = [tube_coord[0] for tube_coord in self.tube_coords]
        velocities_x_components = \
            self.compute_spatial_component_derivative(x_component_coords)
        y_component_coords = [tube_coord[1] for tube_coord in self.tube_coords]
        velocities_y_components = \
            self.compute_spatial_component_derivative(y_component_coords)
        z_component_coords = [tube_coord[2] for tube_coord in self.tube_coords]
        velocities_z_components = \
            self.compute_spatial_component_derivative(z_component_coords)
        self.velocities = np.transpose(np.array([velocities_x_components,
                                                 velocities_y_components,
                                                 velocities_z_components])

    def compute_accelerations_components(self):
        self.accelerations_x_components = \
        self.compute_spatial_component_derivative(self.velocities_x_components)
        self.accelerations_y_components = \
        self.compute_spatial_component_derivative(self.velocities_y_components)
        self.accelerations_z_components = \
        self.compute_spatial_component_derivative(self.velocities_z_components)


    def __init__(self, velocity_profile):
        self.time_check_points = 


def compute_acceleration_in_passenger_frame(velocities_vectors,
                                         accelerations_vectors):
    """
    For an exposition of the method see:
    https://en.wikipedia.org/wiki/Frenet%E2%80%93Serret_formulas

    Find acceleration in passenger frame:
       {t_i}, {v_i}, {a_i}  -->  {T_i}, {N_i}, {B_i} -->  {ap_i}
    """
    #tangent_vectors = [velocity_vector / np.linalg.norm(velocity_vector)
    #                  for velocity_vector in velocities_vectors]
    tangent_vectors = np.divide(velocities_vectors,
                                np.linalg.norm(velocities_vectors, axis=0))
    accel_vel_cross_prod = np.cross(accelerations_vectors, velocities_vectors)
    vel_accel_cross_prod = np.cross(velocities_vectors, accelerations_vectors)
    tangent_vectors_derivatives = np.cross(velocities_vectors, 
                                           accel_vel_cros_prod)
    normal_vectors = np.divide(tangent_vectors_derivatives,
                         np.linalg.norm(tangent_vectors_derivatives, axis=0))
    binormal_vectors = np.divide(vel_accel_cross_prod,
                           np.linalg.norm(vel_accel_cross_prod, axis=0))
    #normal_vectors = [np.cross(vel[i], np.cross(accel[i], vel[i])) /
    #                 np.linalg.norm(
    #                     np.cross(vel[i], np.cross(accel[i], vel[i])))
    #                 for i in range(len(vel))]
    #binormal_vectors = [np.cross(tangent_vector[i], normal_vector[i])
    #                   for i in range(len(vel))]

    # Change of basis matrices for transforming to the tangent, normal, binormal
    # (passenger) frames.
    change_of_basis_matrices = [np.linalg.inv(np.matrix.transpose(
                                np.array([tangent_vector[i],
                                           normal_vector[i],
                                         binormal_vector[i]])))
                                for i in range(len(vel))]

    # Apply change of basis to write the acceleration in tangent, normal, binormal
    # (passenger) frame.
    accelerations_vectors_in_passenger_frame = [
            np.dot(change_of_basis_matrix[i], accelerations_vectors[i])
            for i in range(len(accelerations_vectors))]
    return accelerations_vectors_in_passenger_frame

def get_vertical_weighting_factor(frequency):
    vertical_weighting_factor = 0.588 * math.sqrt(
        (1.911 * frequency**2 + (.25 * frequency**2)**2) /
        ((1 - 0.2777 * frequency**2)**2 +
            (1.563 * frequency - 0.0368 * frequency**3)**2))
    return vertical_weighting_factor

def get_horizontal_weighting_factor(frequency):
    horizontal_weighting_factor = 1.25 * vertical_weighting_factor(frequency)
    return horizontal_weighting_factor

def get_weighting_factors(frequency):
    """
    See (Gangadharan) equations (7) and (8) for weighting factors.
    """
    vertical_weighting_factor = get_vertical_weighting_factor(frequency)
    horizontal_weighting_factor = get_horizontal_weighting_factor(frequency)
    weighting_factors = [0, vertical_weighting_factor,
                            horizontal_weighting_factor]
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
    frequency_weighted_r_m_s = np.sqrt(sum(
        [np.absolute(accel_val)**2 for accel_val in accel_frequency_weighted]))
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


def compute_Lp_norm(t, x, p):
    """Computes the discrete L^p norm of a given list of elements
    """
    summand = [(x[i]**p) * (t[i] - t[i - 1]) for i in range(1, len(t))]
    riemann_sum = sum(summand) / t[-1]
    return riemann_sum**(1. / p)

def comfort_profile_to_comfort_rating(comfort_profile):    
    comfort_rating = compute_Lp_norm(t_comfort, comfort_profile, LP_NORM_POWER)
    return comfort_rating


def partition_list(a_list, partition_length):
    """Breaks up a list of data points into chunks n-elements long
    """
    partition_length = max(1, partition_length)
    partitions = [a_list[i:i + partition_length] for i
                  in range(0, len(a_list), partition_length)]
    return partitions


