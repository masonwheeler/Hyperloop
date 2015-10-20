"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import scipy.signal

# Custom Modules:
import parameters
import smoothing_interpolate


class NaiveTubeProfile(object):

    def compute_tube_elevations(self, arc_lengths, land_elevations):
        land_elevation_peaks_indices_tuple = scipy.signal.argrelmax(
                                          land_elevations, order=10)
        land_elevation_peaks_indices = \
            land_elevation_peaks_indices_tuple[0].tolist()
        tube_elevations = \
            smoothing_interpolate.bounded_curvature_extrema_interpolate(
             arc_lengths, land_elevations, land_elevation_peaks_indices,
                                      parameters.MAX_VERTICAL_CURVATURE)
    
    def __init__(self, elevation_profile):
        arc_lengths = elevation_profile.arc_lengths
        land_elevations = elevation_profile.land_elevations
        tube_elevations = self.compute_tube_elevations(arc_lengths, 
                                                       land_elevations)
        
