"""
Port of match_landscape for testing
"""

#Standard Modules:
import numpy as np
import scipy.interpolate

#Custom Modules:
import config
import parameters

#Fix Spatial_Elevation_Profile
class TubeElevationProfile(object):

    def sort_elevations_indices(elevations_indices):
        sorted_land_elevations_indices = sorted(elevations_indices,
               key=lambda i: self.land_elevations[i], reverse=True)
        sorted_interior_elevations_indices = [index + 1 for index in 
                                              sorted_elevations_indices]
        return sorted_interior_elevations_indices

    def test_elevations_pair_v1(self, elevation_a, arc_length_a,
                                      elevation_b, arc_length_b):
         
    
    def test_elevation_indices_pair(self, elevation_index_a, elevation_index_b):
        if self.index_pairs_tested[elevation_index_a][elevation_index_b]:
            return True
        else:
            self.index_pairs_tested[elevation_index_a][elevation_index_b] = True
            self.index_pairs_tested[elevation_index_b][elevation_index_a] = True
            elevation_a = self.land_elevations[elevation_index_a]
            arc_length_a = self.arc_lengths[elevation_index_a]
            elevation_b = self.land_elevations[elevation_index_b]
            arc_length_b = self.arc_lengths[elevation_index_b]
            are_elevations_compatible = self.test_elevations_pair_v1(
                elevation_a, arc_length_a, elevation_b, arc_length_b)
            return arc_elevations_compatible
    
    def test_elevation_index(self, elevation_index):
        position_of_trial_index = util.sorted_insert(elevation_index,
                                    self.selected_elevations_indices)
        backward_index = self.selected_elevations_indices[
                                  position_of_trial_index - 1]
        trial_index = self.selected_elevations_indices[position_of_trial_index]
        forward_index = self.selected_elevations_indices[
                                  position_of_trial_index + 1]
        backward_compatibility = self.test_elevation_indices_pair(
                                          backward_index, trial_index)
        forward_compatibility = self.test_elevation_indices_pair(trial_index,
                                                               forward_index)
        elevation_index_compatible = (backward_compatibility and
                                       forward_compatiblity)
        self.selected_elevations_indices.pop(position_of_trial_index)
        return elevation_index_compatible        
        
    def add_compatible_land_elevation_to_profile(self):
        for i in range(len(self.sorted_interior_elevations_indices)):
            trial_index = self.sorted_interior_elevations_indices[i]
            is_trial_index_compatible = self.test_elevation_index(trial_index)
            if is_trial_index_compatible:
                trial_index = sorted_interior_elevations_indices.pop(i)
                util.sorted_insert(trial_index, selected_elevations_indices)
                return True
        return False

    def get_tube_elevation_profile_waypoints(self):
        self.selected_elevations_indices = []
        start_elevation_index = 0
        self.selected_elevations_indices.append(start_elevation_index)
        final_elevation_index = len(self.land_elevations) - 1
        self.selected_elevations_indices.append(final_elevation_index)
        interior_land_elevations = land_elevations[1: final_elevation_index]
        self.sorted_interior_land_elevations_indices = \
            self.sort_elevations_indices(interior_land_elevations)
        self.index_pairs_tested = [[0 for i in range(len(self.land_elevations))]
                                      for j in range(len(self.land_elevations))]
        while True:
            added_compatible_elevation = \
                self.add_compatible_elevation_to_profile()
            if added_compatible_elevation:
                pass
            else:
                break
        waypoint_arc_lengths = [self.arc_lengths[index] for index 
                                in self.selected_elevations_indices]
        waypoint_land_elevations = [self.land_elevations[index] for index
                                    in self.selected_elevations_indices]
        return [waypoint_arc_lengths, waypoint_land_elevations]

    def interpolate_tube_elevation_waypoints_v1(self, waypoint_arc_lengths,
                                                 waypoint_land_elevations):
        tube_elevation_spline = scipy.interpolate.PchipInterpolator(
                            waypoint_arc_lengths, waypoint_max_elevations)
        return tube_elevation_spline
    
    def build_tube_elevations_v1(self):
        waypoint_arc_lengths, waypoint_land_elevations = \
            self.get_elevation_profile_waypoints()
        tube_elevation_spline = self.interpolate_elevation_waypoints_v1(
                        waypoint_arc_lengths, waypoint_land_elevations)
        tube_elevations = tube_elevation_spline(self.arc_lengths)
        return tube_elevations
        























