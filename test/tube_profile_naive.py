"""
Original Developer: Jonathan Ward
"""


import parameters


class TubeProfileNaive(object):

    DEFAULT_MAX_CURVATURE = (parameters.MAX_VERTICAL_ACCEL /
                             parameters.MAX_SPEED**2)

    def get_peaks(self):
        

    def __init__(self, elevation_profile,
                      max_curvature=None,
                          max_slope=None):
        self.max_slope = max_slope
        if max_curvature == None:
            self.max_curvature = self.DEFAULT_MAX_CURVATURE
        else:
            self.max_curvature = max_curvature
        self.geospatials = elevation_profile.geospatials
        self.latlngs = elevation_profile.latlngs
        self.arc_lengths = elevation_profile.arc_lengths
        self.land_elevations = elevation_profile.land_elevations
        self.tube_elevations, self.tube_elevation_spline = \
            self.build_tube_elevations()        
        
