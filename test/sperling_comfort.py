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
    PARTITION_LENGTH = 180 #Partition into 3 minute intervals

    def partition_list(self, a_list, partition_length):
        """Breaks up a list of data points into chunks n-elements long
        """
        partitions = [a_list[i:i + partition_length] for i
                      in range(0, len(a_list), partition_length)]
        return partitions
    
    @staticmethod
    def get_vertical_weighting_factor(f):
        """
        See (Gangadharan) equations (7) and (8) for weighting factors.
        """
        vertical_weighting_factor = 0.588 * np.sqrt(
                (1.911 * f**2 + (.25 * f**2)**2) /
                ((1 - (0.2777 * f**2))**2 +
                 (1.563 * f - 0.0368 * f**3)**2)
            )
        return vertical_weighting_factor

    def get_lateral_weighting_factor(self, frequency):
        vertical_weighting_factor = \
            SperlingComfortProfile.get_vertical_weighting_factor(frequency)
        lateral_weighting_factor = vertical_weighting_factor * 1.25
        return lateral_weighting_factor
    
    @staticmethod
    def get_component_comfort(frame_component_accels,
             component_weighting_function, time_interval):
        """
        See (Forstberg) equation (3.1) for Sperling Comfort Index equation.
        """
        ##print "accels: "
        ##print frame_component_accels
        frame_component_accels_fft = np.fft.fft(frame_component_accels) 
        ##print "fft: " 
        ##print frame_component_accels_fft
        freqs_spectrum_width = frame_component_accels_fft.shape[0]
        frame_component_accels_freqs = (frame_component_accels_fft /
                                        freqs_spectrum_width)
        ##print "entire freqs: "
        ##print frame_component_accels_freqs
        ##frame_component_accels_real_freqs = np.real(
        ##                    frame_component_accels_freqs)
        ##frame_component_accels_imag_freqs = np.imag(
        ##                    frame_component_accels_freqs)
        ##print "real freqs: "
        ##print np.amax(frame_component_accels_real_freqs)
        ##print frame_component_accels_real_freqs
        ##print "imag freqs: "
        ##print np.amax(frame_component_accels_imag_freqs)
        ##print frame_component_accels_imag_freqs
        positive_width = int(math.ceil(freqs_spectrum_width / 2.0))
        negative_width = int(math.floor(freqs_spectrum_width / 2.0))
        weighting_factors = [component_weighting_function(index/time_interval)
                            for index in range(-negative_width, positive_width)]
        weighting_factors_array = np.array(weighting_factors)
        ##print "weighting factors: " 
        ##print weighting_factors_array
        weighted_component_accels_freqs = np.multiply(weighting_factors_array,
                                                 frame_component_accels_freqs)
        ##print "freqs: "
        ##print weighted_component_accels_freqs
        weighted_component_accels_freqs_rms = np.sqrt(
                                                np.sum(
                                                  np.square(
                                                    np.absolute(
                                              weighted_component_accels_freqs))))
        ##print "rms: " 
        ##print weighted_component_accels_freqs_rms
        component_comfort_rating = 4.42*weighted_component_accels_freqs_rms**0.3
        return component_comfort_rating

    def compute_partition_comfort_rating(self, 
            times_partition, frame_accel_vectors_partition):
        frame_x_accels, frame_y_accels, frame_z_accels = np.transpose(
                                                 frame_accel_vectors_partition)
        time_interval = (times_partition[-1] - times_partition[0])
        y_comfort_rating = SperlingComfortProfile.get_component_comfort(
            frame_y_accels, self.get_lateral_weighting_factor, time_interval)
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

    def compute_comfort_profile(self, cumulative_time_steps,
                                       frame_accel_vectors):
        """
        Partition the accels and times.
        """
        total_time = cumulative_time_steps[-1]
        times_partitions = self.partition_list(
                  cumulative_time_steps, self.PARTITION_LENGTH)
        time_checkpoints = [time_partition[-1] for time_partition in
                            times_partitions]
        time_intervals = [(time_partition[-1] - time_partition[0])
                          for time_partition in times_partitions]
        frame_accel_vectors_partitions = self.partition_list(
                      frame_accel_vectors, self.PARTITION_LENGTH)
        comfort_profile = [self.compute_partition_comfort_rating(
                                             times_partitions[i], 
                               frame_accel_vectors_partitions[i])
                           for i in range(len(times_partitions))]
        comfort_rating = self.compute_lp_norm(total_time, time_intervals, 
                                              comfort_profile, self.LP_NORM_POWER)
        return [comfort_profile, comfort_rating, time_checkpoints]

    def __init__(self, passenger_frame):
        cumulative_time_steps = passenger_frame.cumulative_time_steps
        frame_accels_vectors = passenger_frame.frame_accels_vectors
        comfort_profile, comfort_rating, time_checkpoints = \
           self.compute_comfort_profile(cumulative_time_steps, 
                                         frame_accels_vectors)
        self.time_checkpoints = time_checkpoints
        self.comfort_profile = comfort_profile
        self.comfort_rating = comfort_rating

def wz(f):
    return 0.588*math.sqrt((1.911 * f**2 + (.25 * f**2)**2) / ((1 - 0.2777 *f**2)**2 + (1.563 * f - 0.0368 * f**3)**2))

def w(f):
    return [0, wz(f), 1.25 * wz(f)]

def fw_RMS(af, T, mu):
    N = len(af)+0.0
    T = T+0.0
    L = int(math.floor(N/2))
    awf = [w(m/T)[mu] * af[m] for m in range(-L, L+1)]
    Sum = sum([np.absolute(accel)**2 for accel in awf])
    return Sum

#def comfort(v, a, T, mu):
def comfort(a, T, mu):
    #N = len(v)
    N = len(a)
    #al = aPassenger(v, a, mu)
    alf = np.fft.fft(a) / N
    afw_RMS = fw_RMS(alf, T, mu)
    return 4.42*(afw_RMS)**0.3


def sperling_test_function(f):
    test_value = 2.10173 * (
                           (7.97828 * f**4 + 243.944 * f**2) /
                           (f**6 - 28.006 * f**4 + 1393.82 * f**2 + 738.422)
                           )**0.15
    return test_value

def get_monofrequency_accels(f, t):
    times = np.arange(0, t, 0.0005)
    ##print times
    args = 2 * np.pi * f * times
    ##print args
    accels = np.sin(args)
    ##print accels
    return accels

def test_sperling_comfort_index(f, n):
    t = float(n) / float(f)
    accels = get_monofrequency_accels(f, t)
    operator = SperlingComfortProfile.get_vertical_weighting_factor
    component_comfort = SperlingComfortProfile.get_component_comfort(
                                                 accels, operator, t)
    test_value = sperling_test_function(f)
    mu = 1
    old_comfort_value = comfort(accels, t, mu)
    print old_comfort_value
    print component_comfort
    print test_value


N = 10.0
F = 0.1

test_sperling_comfort_index(F, N)
