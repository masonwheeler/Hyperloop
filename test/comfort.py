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
    PARTITION_LENGTH = 500

    def numerical_derivative(self, f, t):
        """Implements a numerical derivative
        """
        N = len(f)
        df = [0] * N
        for i in range(1, N - 1):
            df[i] = 0.5 * ((f[i + 1] - f[i]) / (t[i + 1] - t[i]) +
                           (f[i] - f[i - 1]) / (t[i] - t[i - 1]))
        df[0] = (f[1] - f[0]) / (t[1] - t[0])
        df[N - 1] = (f[N - 1] - f[N - 2]) / (t[N - 1] - t[N - 2])
        return df

    def compute_component_derivative(self, spatial_component_coords):
        spatial_component_derivative = self.numerical_derivative(
                        spatial_component_coords, self.time_checkpoints)
        return spatial_component_derivative

    def compute_velocities_vectors(self, tube_coords):
        x_component_coords = [tube_coord[0] for tube_coord in tube_coords]
        self.velocities_x_components = \
            self.compute__component_derivative(x_component_coords)
        y_component_coords = [tube_coord[1] for tube_coord in tube_coords]
        self.velocities_y_components = \
            self.compute_component_derivative(y_component_coords)
        z_component_coords = [tube_coord[2] for tube_coord in tube_coords]
        self.velocities_z_components = \
            self.compute__component_derivative(z_component_coords)
        self.velocities_vectors = np.transpose(np.array([
                                      self.velocities_x_components,
                                      self.velocities_y_components,
                                      self.velocities_z_components])

    def compute_accelerations_vectors(self):
        accelerations_x_components = \
        self.compute_spatial_component_derivative(self.velocities_x_components)
        accelerations_y_components = \
        self.compute_spatial_component_derivative(self.velocities_y_components)
        accelerations_z_components = \
        self.compute_spatial_component_derivative(self.velocities_z_components)
        self.accelerations_vectors = np.transpose(np.array([
                                         accelerations_x_components,
                                         accelerations_y_components,
                                         accelerations_z_components])

    def compute_accelerations_vectors_in_passenger_frame(self):
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
        passenger_accels_vectors = [
            np.dot(change_of_basis_matrix[i], accelerations_vectors[i])
            for i in range(len(accelerations_vectors))]
        (self.passenger_tangent_accels,
         self.passenger_normal_accels,
         self.passenger_binormal_accels) = \
            np.transpose(passenger_accels_vectors)
        self.passenger_accels_magnitudes = [np.linalg.norm(accel_vector)
                            for accel_vector in passenger_accels_vectors]
        

    def get_vertical_weighting_factor(self, frequency):
        vertical_weighting_factor = 0.588 * math.sqrt(
                (1.911 * frequency**2 + (.25 * frequency**2)**2) /
                ((1 - 0.2777 * frequency**2)**2 +
                 (1.563 * frequency - 0.0368 * frequency**3)**2)
            )
        return vertical_weighting_factor

    def get_lateral_weighting_factor(self, frequency):
        vertical_weighting_factor = self.get_vertical_weighting_factor(
                                                                frequency)
        lateral_weighting_factor = 1.25 * vertical_weighting_factor
        return horizontal_weighting_factor

    def get_weighting_factors(self, frequency):
        """
        See (Gangadharan) equations (7) and (8) for weighting factors.
        """
        vertical_weighting_factor = self.get_vertical_weighting_factor(
                                                                frequency)
        lateral_weighting_factor = self.get_lateral_weighting_factor(frequency)
        weighting_factors = [0, vertical_weighting_factor,
                                 lateral_weighting_factor]
        return weighting_factors

    def partition_list(self, a_list, partition_length):
        """Breaks up a list of data points into chunks n-elements long
        """
        partition_length = max(1, partition_length)
        partitions = [a_list[i:i + partition_length] for i
                      in range(0, len(a_list), partition_length)]
        return partitions

    def partition_passenger_accelerations(self):
        time_interval_partitions = self.partition_list(self.time_checkpoints,
                                                       self.PARTITION_LENGTH)
        self.passenger_tangent_accels_partitions = self.partition_list(
                        self.passenger_tangent_accels, self.PARTITION_LENGTH)
        self.passenger_normal_accels_partitions = self.partition_list(
                        self.passenger_normal_accels, self.PARTITION_LENGTH)
        self.passenger_binormal_accels_partitions = self.partition_list(
                        self.passenger_binormal_accels, self.PARTITION_LENGTH)
        self.passenger_accels_magnitudes_partitions = self.partition_list(
                        self.passenger_accels_magnitudes, self.PARTITION_LENGTH)
    
    def compute_passenger_acceleration_frequencies(self):
        self.passenger_tangent_accels_frequencies_partitions = [
            np.fft.fft(passenger_tangent_accels_partition)
            for passenger_tangent_accels_partition
             in self.passenger_tangent_accels_partitions]
        self.passenger_normal_accels_frequencies_partitions = [
            np.fft.fft(passenger_normal_accels_partition)
            for passenger_normal_accels_partition
             in self.passenger_normal_accels_partitions]
        self.passenger_binormal_accels_frequencies_partitions = [
            np.fft.fft(passenger_binormal_accels_partition)
            for passenger_binormal_accels_partition
             in self.passenger_binormal_accels_partitions]
        self.passenger_accels_magnitudes_frequencies_partitions = [
            np.fft.fft(passenger_accels_magnitudes_partition)
            for passenger_accels_magnitudes_partition
             in self.passenger_accels_magnitudes_partitions]

    def compute_frequency_weighted_accelerations(self, frequencies_partitions):
        frequency_widths = [float(len(frequencies_partition)) for
                            frequencies_partition in frequencies_partitions]
        frequency_half_widths = [int(math.float(frequency_width / 2.0))
                                 for frequency_width in frequency_half_widths]
        self.frequency_weighted_passenger_y_accels = \
             [self.get_lateral_weighting_factor(frequency_index / time_interval)
              * frequency_index for frequency_index in
              range(-frequency_half_width, frequency_half_width + 1)]
        self.frequency_weighted_passenger_z_accels = \
             [self.get_lateral_weighting_factor(frequency) * frequency for
              frequency in self.passenger_x_accel_frequencies]
        

    def compute_frequency_weighted_rms(self, accel_frequency, time_interval, component):
        """
        See (Forstberg) equation (3.1) for Sperling Comfort Index equation.
        """
        frequency_width = float(len(accel_frequency))
        time_interval = float(time_interval)
        frequency_half_width = int(math.floor(frequency_width / 2.0))
        accel_frequency_weighted = [
            (weighting_factors(frequency_index / time_interval)
             * accel_frequency[frequency_index]) for frequency_index
            in range(-frequency_half_width, frequency_half_width + 1)]
        frequency_weighted_r_m_s = np.sqrt(sum(
            [np.absolute(accel_val)**2 for accel_val in accel_frequency_weighted]))
        return frequency_weighted_r_m_s

    def compute_sperling_comfort_index(passenger_accels_vectors,
                                                    time_interval):
        """
        2. Take Fast Fourier Transform of psnger accel:
              {ap_i}  -->  {ap_f}
        3. Apply weighting filter and sum results
              {ap_f} --> {w(f)*ap_f} --> c = sum_f |w(f)|^2
        """
        num_time_points = len(passenger_accels_component)
        accel_passenger_frequency = (np.fft.fft(passenger_accels_component) /
                                     num_time_points)
        accel_frequency_weighted_r_m_s = frequency_weighted_rms(
            accel_passenger_frequency, time_interval, component)
        sperling_comfort_index = 4.42 * (accel_frequency_weighted_r_m_s)**0.3
        return sperling_comfort_index

    def compute_Lp_norm(self, t, x, p):
        """Computes the discrete L^p norm of a given list of elements
        """
        summand = [(x[i]**p) * (t[i] - t[i - 1]) for i in range(1, len(t))]
        riemann_sum = sum(summand) / t[-1]
        return riemann_sum**(1. / p)

    def comfort_profile_to_comfort_rating(self, comfort_profile):    
        comfort_rating = compute_Lp_norm(t_comfort, comfort_profile,
                                                 self.LP_NORM_POWER)
        return comfort_rating

    def __init__(self, velocity_profile, tube_coords):
        self.time_check_points = velocity_profile.time_check_points
        self.compute_velocities_vectors()
        self.compute_accelerations_vectors()
        self.compute_accelerations_vectors_in_passenger_frame()








