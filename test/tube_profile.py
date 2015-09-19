"""
Port of match_landscape for testing
"""

#Standard Modules:
import numpy as np
import scipy.interpolate

#Custom Modules:
import clothoid
import config
import curvature
import parameters
import pylon_cost
import tube_cost
import util
import velocity


class TubeProfile(object):

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
        is_elevation_pair_valid = slope < self.slope_constraint
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
        position_of_trial_index = util.sorted_insert(elevation_index,
                                    self.selected_land_elevations_indices)
        backward_index = self.selected_land_elevations_indices[
                                   position_of_trial_index - 1]
        trial_index = self.selected_land_elevations_indices[
                                    position_of_trial_index]
        forward_index = self.selected_land_elevations_indices[
                                  position_of_trial_index + 1]
        backward_compatibility = self.test_land_elevation_indices_pair(
                                           backward_index, trial_index)
        forward_compatibility = self.test_land_elevation_indices_pair(
                                           trial_index, forward_index)
        elevation_index_compatible = (backward_compatibility and
                                       forward_compatibility)
        self.selected_land_elevations_indices.pop(position_of_trial_index)
        return elevation_index_compatible        
        
    def add_compatible_land_elevation_to_waypoints(self):
        for i in range(len(self.sorted_interior_land_elevations_indices)):
            trial_index = self.sorted_interior_land_elevations_indices[i]
            is_trial_index_compatible = self.test_land_elevation_index(
                                                           trial_index)
            if is_trial_index_compatible:
                trial_index = \
                  self.sorted_interior_land_elevations_indices.pop(i)
                util.sorted_insert(trial_index,
                                   self.selected_land_elevations_indices)
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

    def interpolate_tube_elevation_waypoints_v1(self, waypoint_arc_lengths,
                                                 waypoint_land_elevations):
        tube_elevation_spline = scipy.interpolate.PchipInterpolator(
                            waypoint_arc_lengths, waypoint_land_elevations)
        return tube_elevation_spline
    
    def build_tube_elevations_v1(self):
        waypoint_arc_lengths, waypoint_land_elevations = \
            self.get_tube_elevation_profile_waypoints()
        tube_elevation_spline = self.interpolate_tube_elevation_waypoints_v1(
                              waypoint_arc_lengths, waypoint_land_elevations)
        tube_elevations = tube_elevation_spline(self.arc_lengths)
        return [tube_elevations, tube_elevation_spline]

    def compute_time_v1(self):
        self.tube_curvature = curvature.compute_curvature_pchip(
                   self.tube_elevation_spline, self.arc_lengths)
        self.max_allowed_vels = \
            curvature.curvature_array_to_bounded_max_allowed_vels(
               self.tube_curvature, parameters.MAX_VERTICAL_ACCEL,
                                    parameters.MAX_SPEED)
        self.time = velocity.compute_trip_time(self.max_allowed_vels,
                                          self.arc_lengths[1])
        
    def build_pylons(self):
        self.pylon_heights = util.subtract(self.tube_elevations,
                                          self.land_elevations)
        pylon_costs = [pylon_cost.compute_pylon_cost_v1(pylon_height)
                       for pylon_height in self.pylon_heights]
        self.pylons = [{"geospatial" : self.geospatials[i],
                        "latlng" : self.latlngs[i],
                        "landElevation" : self.land_elevations[i],
                        "pylonHeight" : self.pylon_heights[i],
                        "pylonCost" : pylon_costs[i]}
                        for i in range(len(self.pylon_heights))]
        self.pylon_cost = sum(pylon_costs)

    def get_tube_coords(self):
        geospatial_x_vals, geospatial_y_vals = zip(*self.geospatials)
        self.tube_coords = zip(geospatial_x_vals, geospatial_y_vals,
                                                    self.tube_elevations)

    def compute_tube_cost(self):
        self.tube_cost = tube_cost.compute_tube_cost_v1(self.tube_coords)
  
        
    #def __init__(self, elevation_profile, curvature_constraint):
    #def __init__(self, elevation_profile, slope_constraint):
    def __init__(self, elevation_profile):
        #self.curvature_constraint = curvature_constraint
        #self.slope_constraint = slope_constraint
        self.max_curvature = \
            parameters.MAX_VERTICAL_ACCEL / parameters.MAX_SPEED**2
        self.geospatials = elevation_profile.geospatials
        self.latlngs = elevation_profile.latlngs
        self.arc_lengths = elevation_profile.arc_lengths
        self.land_elevations = elevation_profile.land_elevations
        self.tube_elevations, self.tube_elevation_spline = \
            self.build_tube_elevations_v1()
        self.compute_time_v1()
        self.get_tube_coords()
        self.compute_tube_cost()
        self.build_pylons()
        
        






















