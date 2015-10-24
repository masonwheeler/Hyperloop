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

    def get_vertical_weighting_factor(self, frequency):
        """
        See (Gangadharan) equations (7) and (8) for weighting factors.
        """
        vertical_weighting_factor = 0.588 * np.sqrt(
                (1.911 * frequency**2 + (.25 * frequency**2)**2) /
                ((1 - 0.2777 * frequency**2)**2 +
                 (1.563 * frequency - 0.0368 * frequency**3)**2)
            )
        return vertical_weighting_factor

    def get_lateral_weighting_factor(self, frequency):
        vertical_weighting_factor = self.get_vertical_weighting_factor(
                                                              frequency)
        lateral_weighting_factor = vertical_weighting_factor * 1.25
        return lateral_weighting_factor

    def get_component_comfort(self, frame_component_accels,
             component_weighting_function, time_interval):
        """
        See (Forstberg) equation (3.1) for Sperling Comfort Index equation.
        """
        frame_component_accels_fft = np.fft.rfft(frame_component_accels) 
        freqs_spectrum_width = frame_component_accels_fft.shape[0]
        frame_component_accels_freqs = (frame_component_accels_fft /
                                        freqs_spectrum_width)
        frame_component_accels_real_freqs = np.real(
                            frame_component_accels_freqs)
        positive_width = int(math.ceil(freqs_spectrum_width / 2.0))
        negative_width = int(math.floor(freqs_spectrum_width / 2.0))
        weighting_factors = [component_weighting_function(index/time_interval)
                            for index in range(-negative_width, positive_width)]
        weighting_factors_array = np.array(weighting_factors)        
        weighted_component_accels_freqs = np.dot(weighting_factors_array,
                                       frame_component_accels_real_freqs)
        weighted_component_accels_freqs_rms = np.sqrt(np.sum(np.square(
                                        weighted_component_accels_freqs)))
        component_comfort_rating = 4.42*weighted_component_accels_freqs_rms**0.3
        return component_comfort_rating

    def compute_partition_comfort_rating(self, 
            times_by_arc_length_partition, frame_accel_vectors_partition):
        frame_x_accels, frame_y_accels, frame_z_accels = np.transpose(
                                                 frame_accel_vectors_partition)
        time_interval = (times_by_arc_length_partition[-1] - 
                         times_by_arc_length_partition[0])
        y_comfort_rating = self.get_component_comfort(frame_y_accels, 
                    self.get_lateral_weighting_factor, time_interval)
        z_comfort_rating = self.get_component_comfort(frame_z_accels, 
                    self.get_lateral_weighting_factor, time_interval)
        total_comfort_rating = np.sqrt(y_comfort_rating**2 + 
                                       z_comfort_rating**2)
        return total_comfort_rating

    def compute_lp_norm(self, total_time, time_intervals, x, p):
        """Computes the discrete L^p norm of a given list of elements
        """
        summand = [(x[i]**p) * (time_intervals[i]) for i in range(len(x))]
        riemann_sum = sum(summand) / total_time
        lp_norm = riemann_sum**(1. / p)
        return lp_norm

    def compute_comfort_profile(self, times_by_arc_lengths,
                                       frame_accel_vectors):
        """
        Partition the accels and times.
        """
        total_time = times_by_arc_lengths[-1]
        times_by_arc_lengths_partitions = self.partition_list(
                  times_by_arc_lengths, self.PARTITION_LENGTH)
        time_checkpoints = [time_partition[-1] for time_partition in
                            times_by_arc_lengths_partitions]
        time_intervals = [(time_partition[-1] - time_partition[0])
                          for time_partition in times_by_arc_lengths_partitions]
        frame_accel_vectors_partitions = self.partition_list(
                      frame_accel_vectors, self.PARTITION_LENGTH)
        comfort_profile = [self.compute_partition_comfort_rating(
                               times_by_arc_lengths_partitions[i], 
                               frame_accel_vectors_partitions[i])
                           for i in range(len(times_by_arc_lengths_partitions))]
        comfort_rating = self.compute_lp_norm(total_time, time_intervals, 
                                              comfort_profile, self.LP_NORM_POWER)
        return [comfort_profile, comfort_rating, time_checkpoints]

    def __init__(self, passenger_frame):
        times_by_arc_length = passenger_frame.times_by_arc_length
        frame_accels_vectors = passenger_frame.frame_accels_vectors
        comfort_profile, comfort_rating, time_checkpoints = \
        self.compute_comfort_profile(times_by_arc_length, frame_accels_vectors)
        self.time_checkpoints = time_checkpoints
        self.comfort_profile = comfort_profile
        self.comfort_rating = comfort_rating
