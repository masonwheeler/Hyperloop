"""
Original Developer: David Roberts
Purpose of Module: To evaluate passenger comfort using
                   Sperling's comfort index (Wz).

Last Modification Purpose: To clarify naming and add citations.

Citations:
   "Ride comfort in Tilting Trains"
    - Johan Forstberg
   "Experimental and Analytical Ride Comfort Evaluation of a Railway Coach"
    - K. V. Gangadharan

"""

# Standard Modules:
import math
import numpy as np


class SperlingComfortProfile(object):

    LP_NORM_POWER = 10
    PARTITION_LENGTH = 500

    def partition_list(self, a_list, partition_length):
        """Breaks up a list of data points into chunks n-elements long
        """
        partitions = [a_list[i:i + partition_length] for i
                      in range(0, len(a_list), partition_length)]
        return partitions

    def partition_passenger_accelerations(self, times_by_arc_lengths,
                                                frame_accel_vectors):
        """
        With the Frenet-Serret frame currently used, the normal vector
        is the vertical direction for the pod, and the binormal vector
        is the lateral direction.
        """        
        times_by_arc_lengths_partitions = self.partition_list(
                  times_by_arc_lengths, self.PARTITION_LENGTH)
        frame_accel_vectors_partitions = self.partition_list(
                      frame_accel_vectors, self.PARTITION_LENGTH)
        return frame_accels_vectors_partitions

    def compute_partition_comfort_value(self, 
            times_by_arc_length_partition, frame_accel_vectors_partition):
        frame_x_accels, frame_y_accels, frame_z_accels = np.transpose(
                                                 frame_accel_vectors_partition)
        frame_x_accels_frequencies = np.fft.fft(frame_x_accels)
        frame_y_accels_frequencies = np.fft.fft(frame_y_accels)
        frame_z_accels_frequencies = np.fft.fft(frame_z_accels)        

    def get_vertical_weighting_factor(self, frequency):
        vertical_weighting_factor = 0.588 * math.sqrt(
                (1.911 * frequency**2 + (.25 * frequency**2)**2) /
                ((1 - 0.2777 * frequency**2)**2 +
                 (1.563 * frequency - 0.0368 * frequency**3)**2)
            )
        return vertical_weighting_factor

    def get_weighting_factors(self, frequency):
        """
        See (Gangadharan) equations (7) and (8) for weighting factors.
        """
        vertical_weighting_factor = self.get_vertical_weighting_factor(
                                                                frequency)
        lateral_weighting_factor = vertical_weighting_factor * 1.25
        weighting_factors = np.array([0, vertical_weighting_factor,
                                          lateral_weighting_factor])
        return weighting_factors

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

    def __init__(self, passenger_frame):

