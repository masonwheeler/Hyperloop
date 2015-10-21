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
        weighting_factors = np.array([0, vertical_weighting_factor,
                                          lateral_weighting_factor])
        return weighting_factors

    def partition_list(self, a_list, partition_length):
        """Breaks up a list of data points into chunks n-elements long
        """
        partition_length = max(1, partition_length)
        partitions = [a_list[i:i + partition_length] for i
                      in range(0, len(a_list), partition_length)]
        return partitions

    def partition_passenger_accelerations(self):
        """
        With the Frenet-Serret frame currently used, the normal vector
        is the vertical direction for the pod, and the binormal vector
        is the lateral direction.
        """
        self.time_interval_partitions = self.partition_list(
                    self.time_checkpoints, self.PARTITION_LENGTH)
        self.passenger_normal_accels_partitions = self.partition_list(
                        self.passenger_normal_accels, self.PARTITION_LENGTH)
        self.passenger_binormal_accels_partitions = self.partition_list(
                        self.passenger_binormal_accels, self.PARTITION_LENGTH)

        self.passenger_accels_vectors_partitions = self.partition_list(
                        self.passenger_accels_vectors, self.PARTITION_LENGTH)
        self.passenger_accels_magnitudes_partitions = self.partition_list(
                        self.passenger_accels_magnitudes, self.PARTITION_LENGTH)
    
    def compute_passenger_acceleration_frequencies(self):
        """
        With the Frenet-Serret frame currently used, the normal vector
        is the vertical direction for the pod, and the binormal vector
        is the lateral direction.
        """
        self.passenger_normal_accels_frequencies_partitions = [
            np.fft.fft(passenger_normal_accels_partition)
            for passenger_normal_accels_partition
             in self.passenger_normal_accels_partitions]
        self.passenger_binormal_accels_frequencies_partitions = [
            np.fft.fft(passenger_binormal_accels_partition)
            for passenger_binormal_accels_partition
             in self.passenger_binormal_accels_partitions]

    def compute_passenger_acceleration_frequencies_v2(self):
        self.passenger_accels_magnitudes_frequencies_partitions = [
            np.fft.fft(passenger_accels_magnitudes_partition)
            for passenger_accels_magnitudes_partition
             in self.passenger_accels_magnitudes_partitions]

    def compute_frequency_weighted_accelerations(self):
        """
        With the Frenet-Serret frame currently used, the normal vector
        is the vertical direction for the pod, and the binormal vector
        is the lateral direction.
        """        
        self.frequency_weighted_passenger_normal_accels_partitions = []
        self.frequency_weighted_passenger_binormal_accels_partitions = []
        for i in range(len(self.time_interval_partitions)):
            time_interval_partition = self.time_interval_partitions[i]
            time_interval = (time_interval_partition[-1] -
                             time_interval_partition[0])

            normal_frequencies_partition = \
                self.passenger_normal_frequencies_partition[i]
            normal_accels_frequencies_width = float(len(
                                normal_frequencies_partition))
            normal_accels_frequencies_half_width = \
                                    int(math.float(frequency_width / 2.0))
            normal_accels_frequencies_indices_range = \
                    range(-normal_accels_frequencies_half_width,
                           normal_accels_frequencies_half_width + 1)
            frequency_weighted_acceleration = [
                (self.get_vertical_weighting_factor(
                    frequency_index / time_interval) *
                    normal_frequencies_partition[frequency_index])
                for frequency_index in normal_accels_frequencies_indices]
            self.frequency_weighted_passenger_normal_accels_partitions.append(
                frequency_weighted_acceleration)

            binormal_frequencies_partition = \
                self.passenger_normal_frequencies_partition[i]
            binormal_accels_frequencies_width = float(len(
                                binormal_frequencies_partition))
            binormal_accels_frequencies_half_width = \
                                    int(math.float(frequency_width / 2.0))
            binormal_accels_frequencies_indices_range = \
                    range(-binormal_accels_frequencies_half_width,
                           binormal_accels_frequencies_half_width + 1)
            frequency_weighted_acceleration = [
                (self.get_vertical_weighting_factor(
                    frequency_index / time_interval) *
                    binormal_frequencies_partition[frequency_index])
                for frequency_index in binormal_accels_frequencies_indices]
            self.frequency_weighted_passenger_binormal_accels_partitions.append(
                frequency_weighted_acceleration)

    def compute_frequency_weighted_accelerations_v2(self):
        self.frequency_weighted_passenger_accels_partitions = []
        for i in range(len(self.time_interval_partitions)):
            time_interval_partition = self.time_interval_partitions[i]
            time_interval = (time_interval_partition[-1] -
                             time_interval_partition[0])

            passenger_accels_vectors_partition = \
                self.passenger_accels_vectors_partitions[i]

            accel_magnitude_frequency_partition = \
                self.passenger_accels_magnitudes_frequencies_partitions[i]
            frequencies_weights = [self.get_weighting_factors(frequency)
                    for frequency in accel_magnitude_frequency_partition]
            self.frequency_weighted_passenger_accels_partitions = \
                [(np.dot(frequencies_weights[i],
                         self.passenger_accels_vectors_partition[i]) 
                for i in range(len(self.passenger_accels_frequencies
              accels_magnitudes_frequencies_indices]
        
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
        comfort_rating = self.compute_Lp_norm(t_comfort, self.comfort_profile,
                                                 self.LP_NORM_POWER)
        return comfort_rating

    def __init__(self, velocity_profile, tube_coords):
        self.time_check_points = velocity_profile.time_check_points
        self.compute_velocities_vectors()
        self.compute_accelerations_vectors()
        self.compute_accelerations_vectors_in_passenger_frame()








