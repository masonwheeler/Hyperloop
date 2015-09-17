"""
Port of match_landscape for testing
"""

# Standard Modules:
import numpy as np
import scipy.interpolate

# Custom Modules:
import config
import parameters

class VelocityProfile(object):

    MIN_VELOCITY = 10 #Meters/Second

    def sort_velocities_indices(velocities_indices):    
        sorted_velocities_indices = sorted(velocities_indices,
                                  key=lambda i: velocities[i])
        sorted_interior_velocities_indices = [index + 1 for index in
                                              sorted_velocities_indices]
        return sorted_interior_velocities_indices
    
    ""#
    def test_velocities_pair_v1(self, velocity_a, arc_length_a,
                                      velocity_b, arc_length_b):
        velocity_difference = velocity_b - velocity_a
        arc_length_difference = arc_length_a - arc_length_b
        mean_velocity = (velocity_a + velocity_b) / 2.0    
        
        variable_a = self.max_linear_accel / mean_vel
        variable_b = self.jerk_tolerance / mean_vel**2
        
        threshold_arc_length = 2 * variable_a / variable_b
        if arc_length_difference > threshold_arc_length:
            arc_length_tolerance = (arc_length_difference /2)**2 * variable_b
        else:
            arc_length_tolerance = \
                (arc_length_difference - (variable_a /variable_b)) * variable_a
        is_velocity_pair_compatible = \
            arc_length_difference < arc_length_tolerance
        return is_velocity_pair_compatible
    ""#
            
    def test_velocity_indices_pair(self, velocity_index_a, velocity_index_b):
        if self.index_pairs_tested[velocity_index_a][velocity_index_b]:
            return True
        else:
            self.index_pairs_tested[velocity_index_a][velocity_index_b] = True
            self.index_pairs_tested[velocity_index_b][velocity_index_a] = True
            velocity_a = self.max_velocities[velocity_index_a]
            arc_length_a = self.arc_lengths[velocity_index_a]        
            velocity_b = self.max_velocities[velocity_index_b]
            arc_length_b = self.arc_lengths[velocity_index_b]
            are_velocities_compatible = self.test_velocities_pair_v1(velocity_a,
                                         arc_length_a, velocity_b, arc_length_b)
            return are_velocities_compatible
        
    def test_velocity_index(self, velocity_index):
        position_of_trial_index = util.sorted_insert(velocity_index,
                                  self.selected_velocities_indices)
        backward_index = self.selected_velocities_indices[
                                 posiition_of_trial_index - 1]
        trial_index = self.selected_velocities_indices[posiition_of_trial_index]
        forward_index = self.selected_velocities_indices[
                                posiition_of_trial_index + 1]
        backward_compatibility = self.test_velocity_indices_pair(backward_index,
                                                                    trial_index)
        forward_compatibility = self.test_velocity_indices_pair(trial_index,
                                                              forward_index)
        velocity_index_compatible = backward_compatibility and forward_compatiblity
        self.selected_velocities_indices.pop(position_of_trial_index)
        return velocity_index_compatible

    def add_compatible_velocity_to_profile(self):
        for i in range(len(self.sorted_interior_velocities_indices)):
            trial_index = self.sorted_interior_velocities_indices[i]
            is_trial_index_compatible = self.test_velocity_index(trial_index)
            if is_trial_index_compatible:
                trial_index = sorted_interior_velocities_indices.pop(i)
                util.sorted_insert(trial_index, selected_velocities_indices)
                return True
        return False    

    def get_velocity_profile_waypoints(self, arc_lengths, max_velocities)
        self.arc_lengths = arc_lengths
        self.max_velocities = max_velocities
        self.selected_velocities_indices = []
        start_velocity_index = 0
        self.selected_velocities_indices.append(start_velocity_index)
        final_velocity_index = len(velocities) - 1
        self.selected_velocities_indices.append(final_velocity_index)
        interior_velocities = velocities[1: len(velocities) - 1]
        self.sorted_interior_velocities_indices = self.sort_velocities_indices(
                                                           interior_velocities)
        self.index_pairs_tested = [[0 for i in range(len(velocities))]
                                      for j in range(len(velocities))]
        while True:
            added_compatible_vel = self.add_compatible_velocity_to_profile()
            if added_compatible_vel:
                pass
            else:
                break
        waypoint_arc_lengths = [arc_lengths[index] for index
                                in selected_velocities_indices]
        waypoint_velocities = [velocities[index] for index
                               in selected_velocities_indices]
        return [waypoint_arc_lengths, waypoint_velocities]
        
    def interpolate_velocity_waypoints_v1(self, waypoint_arc_lengths,
                                                waypoint_velocities):                
        velocity_spline = scipy.interpolate.PchipInterpolator(
                        waypoint_arc_lengths, waypoint_velocities)
        return velocity_spline
            
    def build_velocities_by_arc_length_v1(self, arc_lengths, max_velocities):
        waypoint_arc_lengths, waypoint_velocities = \
            self.get_velocity_profile_waypoints(arc_lengths, max_velocities)
        velocity_spline = self.interpolate_velocity_waypoints_v1(
                        waypoint_arc_lengths, waypoint_velocities)
        unconstrained_velocities_by_arc_length = velocity_spline(arc_lengths)
        min_velocities = np.empty(len(arc_lengths))
        min_velocities.fill(self.MIN_VELOCITY)
        velocities_by_arc_length = np.max(min_velocities,
                  unconstrained_velocities_by_arc_length)
        return velocities_by_arc_length

    def compute_spatial_path_3d_curvature_v1(self, spatial_path_3d_coords):
        path_radii = curvature.points_list_to_radii(spatial_path_3d_coords)
        path_curvatures = [1.0 / radius for radius in path_radii]
        return path_curvatures

    def curvatures_to_max_velocities_v1(self, spatial_path_curvatures):
        start_max_velocity = end_max_velocity = 0
        interior_max_velocities = [
                         min(np.sqrt(parameters.MAX_LATERAL_ACCEL / curvature),
                             parameters.MAX_SPEED)
                         for curvature in spatial_path_curvature]
        max_velocities = [start_max_velocity] + interior_max_velocities \
                                              + [end_max_velocity]
        return max_velocities

    def compute_spatial_path_3d_max_velocities_v1(self, spatial_path_3d_coords):
        path_curvatures = self.compute_spatial_path_3d_curvature_v1(
                                                 spatial_path_3d_coords)
        max_velocities = self.curvatures_to_max_velocities_v1(path_curvatures)
        return max_velocities
    
    def __init__(self, spatial_path_3d):
        arc_lengths = spatial_path_3d.arc_lengths
        self.max_velocities = self.compute_spatial_path_3d_max_velocities_v1(
                                                      spatial_path_3d.coords)
        self.velocities_by_arc_length = self.build_velocities_by_arc_length_v1(
                                                  arc_lengths, max_velocities)
        
        
