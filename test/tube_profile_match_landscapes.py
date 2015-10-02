"""
Port of match_landscape for testing
"""

#Standard Modules:
import numpy as np
import scipy.interpolate

#Custom Modules:
import clothoid
import curvature
import parameters

class TubeProfileMatchLandscapes(object):

    DEFAULT_MAX_CURVATURE = (parameters.MAX_VERTICAL_ACCEL /
                             parameters.MAX_SPEED**2)

    def sort_elevations_indices(self, interior_land_elevations):
        interior_land_elevations_indices = range(len(interior_land_elevations))
        sorted_interior_land_elevations_indices = sorted(
                            interior_land_elevations_indices,
                   key=lambda i: interior_land_elevations[i],
                                                reverse=True)
        sorted_interior_land_elevations_indices = [index + 1 for index in 
                                  sorted_interior_land_elevations_indices]
        return sorted_interior_land_elevations_indices

    def test_land_elevations_pair_v2(self, elevation_a, arc_length_a,
                                           elevation_b, arc_length_b):
        elevation_difference = elevation_b - elevation_a
        arc_length_difference = arc_length_b - arc_length_a
        slope = np.absolute(elevation_difference / arc_length_difference)
        is_elevation_pair_valid = slope < self.max_slope
        return is_elevation_pair_valid
    
    def test_land_elevations_pair_v1(self, elevation_a, arc_length_a,
                                           elevation_b, arc_length_b):
        theta_0 = 0
        theta_1 = 0
        start_curvature, curvature_per_length, length = \
            clothoid.build_clothoid(arc_length_a, elevation_a, theta_0,
                                    arc_length_b, elevation_b, theta_1)
        extremal_curvatures = [start_curvature,
                               start_curvature + length * curvature_per_length]
        largest_curvature = max(np.absolute(extremal_curvatures))
        is_elevation_pair_valid = largest_curvature < self.max_curvature
        return is_elevation_pair_valid
    
    def test_land_elevation_indices_pair(self, elevation_index_a,
                                               elevation_index_b):
        if self.index_pairs_tested[elevation_index_a][elevation_index_b]:
            return True
        else:
            self.index_pairs_tested[elevation_index_a][elevation_index_b] = True
            self.index_pairs_tested[elevation_index_b][elevation_index_a] = True
            elevation_a = self.land_elevations[elevation_index_a]
            arc_length_a = self.arc_lengths[elevation_index_a]
            elevation_b = self.land_elevations[elevation_index_b]
            arc_length_b = self.arc_lengths[elevation_index_b]
            are_elevations_compatible = self.test_land_elevations_pair_v1(
                     elevation_a, arc_length_a, elevation_b, arc_length_b)
            return are_elevations_compatible
    
    def test_land_elevation_index(self, elevation_index):
        [position_of_elevation_index] = np.searchsorted(
            self.selected_land_elevations_indices, [elevation_index])
        previous_elevation_index = self.selected_land_elevations_indices[
                                   position_of_elevation_index - 1]
        next_elevation_index = self.selected_land_elevations_indices[
                                  position_of_elevation_index]
        is_compatible_with_previous = self.test_land_elevation_indices_pair(
                             previous_elevation_index, elevation_index)
        is_compatible_with_next = self.test_land_elevation_indices_pair(
                                    elevation_index, next_elevation_index)
        is_elevation_index_compatible = (is_compatible_with_previous and
                                         is_compatible_with_next)
        return [is_elevation_index_compatible, position_of_elevation_index]
        
    def add_compatible_land_elevation_to_waypoints(self):
        for i in xrange(len(self.sorted_interior_land_elevations_indices)):
            elevation_index = self.sorted_interior_land_elevations_indices[i]
            is_elevation_index_compatible, position_of_elevation_index = \
                self.test_land_elevation_index(elevation_index)
            if is_elevation_index_compatible:
                self.sorted_interior_land_elevations_indices.pop(i)
                self.selected_land_elevations_indices = np.insert(
                                self.selected_land_elevations_indices,
                         position_of_elevation_index, elevation_index)
                return True
        return False

    def get_tube_elevation_profile_waypoints(self):
        self.selected_land_elevations_indices = []
        start_elevation_index = 0
        self.selected_land_elevations_indices.append(start_elevation_index)
        final_elevation_index = len(self.land_elevations) - 1
        self.selected_land_elevations_indices.append(final_elevation_index)
        interior_land_elevations = self.land_elevations[
                                      1: final_elevation_index]        
        self.sorted_interior_land_elevations_indices = \
            self.sort_elevations_indices(interior_land_elevations)
        self.index_pairs_tested = [[0 for i in range(len(self.land_elevations))]
                                      for j in range(len(self.land_elevations))]
        while True:
            added_compatible_elevation = \
                self.add_compatible_land_elevation_to_waypoints()
            if added_compatible_elevation:
                pass
            else:
                break
        waypoint_arc_lengths = [self.arc_lengths[index] for index 
                                in self.selected_land_elevations_indices]
        waypoint_land_elevations = [self.land_elevations[index] for index
                                    in self.selected_land_elevations_indices]
        return [waypoint_arc_lengths, waypoint_land_elevations]

    def interpolate_tube_elevation_waypoints(self, waypoint_arc_lengths,
                                                 waypoint_land_elevations):
        tube_elevation_spline = scipy.interpolate.PchipInterpolator(
                            waypoint_arc_lengths, waypoint_land_elevations)
        return tube_elevation_spline
    
    def build_tube_elevations(self):
        waypoint_arc_lengths, waypoint_land_elevations = \
            self.get_tube_elevation_profile_waypoints()
        tube_elevation_spline = self.interpolate_tube_elevation_waypoints(
                              waypoint_arc_lengths, waypoint_land_elevations)
        tube_elevations = tube_elevation_spline(self.arc_lengths)
        return [tube_elevations, tube_elevation_spline]

    def compute_curvature(self):
        self.tube_curvature_array = curvature.compute_curvature_pchip(
                             self.tube_elevation_spline, self.arc_lengths)
        
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
        self.compute_curvature()

