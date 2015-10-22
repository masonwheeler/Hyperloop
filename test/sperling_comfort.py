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
        return [times_by_arc_length_partitions, frame_accels_vectors_partitions]

    def get_vertical_weighting_factor(self, frequency):
        """
        See (Gangadharan) equations (7) and (8) for weighting factors.
        """
        vertical_weighting_factor = 0.588 * math.sqrt(
                (1.911 * frequency**2 + (.25 * frequency**2)**2) /
                ((1 - 0.2777 * frequency**2)**2 +
                 (1.563 * frequency - 0.0368 * frequency**3)**2)
            )
        return vertical_weighting_factor

    def get_lateral_weighting_factor(self, frequency):
        vertical_weighting_factor = self.get_vertical_weighting_factor
        lateral_weighting_factor = vertical_weighting_factor * 1.25
        return lateral_weighting_factor

    def get_component_comfort(frame_component_accels,
             component_weighting_function, time_interval):   
        frame_component_accels_fft = np.fft.fft(frame_component_accels)
        frequency_spectrum_width = frame_component_accels_fft.shape[0]
        frame_component_accels_freqs = (frame_component_accels_fft /
                                        frame_spectrum_width)
        half_width = int(math.floor(frequency_spectrum_width / 2.0))
        weighting_factors = [component_weighting_function(index/time_interval)
                             for index in range(-half_width, half_width +1)]
        weighting_factors_array = np.array(weighting_factors)
        weighted_component_accels_freqs = np.dot(weighting_factors,
                                      frame_component_accels_freqs)
        weighted_component_accels_freqs_rms = np.sqrt(np.sum(np.square(
                                        weighted_component_accels_freqs)))
        component_comfort_rating = 4.42*weighted_component_accels_freqs_rms**0.3
        return component_comfort_rating

    def compute_partition_comfort_rating(self, 
            times_by_arc_length_partition, frame_accel_vectors_partition):
        """
        See (Forstberg) equation (3.1) for Sperling Comfort Index equation.
        """
        frame_x_accels, frame_y_accels, frame_z_accels = np.transpose(
                                                 frame_accel_vectors_partition)
        time_interval = (times_by_arc_length_partition[-1] - 
                         times_by_arc_length_partition[0])
        y_comfort_rating = self.get_component_comfort(frame_y_accels, 
                    self.get_lateral_weighting_factor, time_interval)
        z_comfort_rating = self.get_component_comfort(frame_z_accels, 
                    self.get_lateral_weighting_factor, time_interval)
        return [y_comfort_rating, z_comfort_rating]

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
