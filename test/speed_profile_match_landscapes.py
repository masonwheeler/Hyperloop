"""
Port of match_landscape for testing
"""

# Standard Modules:
import numpy as np
import scipy.interpolate

# Custom Modules:
import parameters
import reparametrize_speed


class SpeedProfile(object):

    TIME_STEP_SIZE = 1 #Second

    def sort_speeds_indices(self, interior_max_speeds):
        interior_max_speeds_indices = range(len(interior_max_speeds))
        sorted_interior_max_speeds_indices = sorted(
                             interior_max_speeds_indices,
                     key=lambda i: interior_max_speeds[i])
        sorted_interior_max_speeds_indices = [index + 1 for index in
                                  sorted_interior_max_speeds_indices]
        return sorted_interior_max_speeds_indices
    
    def test_speeds_pair(self, speed_a, arc_length_a,
                               speed_b, arc_length_b):
        speed_difference = speed_b - speed_a
        arc_length_difference = arc_length_a - arc_length_b
        mean_vel = (speed_a + speed_b) / 2.0    
        
        variable_a = self.max_longitudinal_accel / mean_vel
        variable_b = self.jerk_tol / mean_vel**2
        
        threshold_arc_length = 2 * variable_a / variable_b
        if arc_length_difference > threshold_arc_length:
            arc_length_tolerance = (arc_length_difference /2)**2 * variable_b
        else:
            arc_length_tolerance = \
                (arc_length_difference - (variable_a /variable_b)) * variable_a
        is_speed_pair_compatible = \
            arc_length_difference < arc_length_tolerance
        return is_speed_pair_compatible
            
    def test_speed_indices_pair(self, max_speeds, arc_lengths, speed_index_a,
                                                               speed_index_b):
        if self.index_pairs_tested[speed_index_a][speed_index_b]:
            return True
        else:
            self.index_pairs_tested[speed_index_a][speed_index_b] = True
            self.index_pairs_tested[speed_index_b][speed_index_a] = True
            speed_a = max_speeds[speed_index_a]
            arc_length_a = arc_lengths[speed_index_a]        
            speed_b = max_speeds[speed_index_b]
            arc_length_b = arc_lengths[speed_index_b]
            are_speeds_compatible = self.test_speeds_pair(speed_a, arc_length_a, 
                                                          speed_b, arc_length_b)
            return are_speeds_compatible
        
    def test_speed_index(self, speed_index, max_speeds, arc_lengths):
        [position_of_speed_index] = np.searchsorted(
            self.selected_max_speeds_indices, [speed_index])
        previous_speed_index = self.selected_max_speeds_indices[
                                   position_of_speed_index - 1]
        next_speed_index = self.selected_max_speeds_indices[
                                    position_of_speed_index]
        is_compatible_with_previous = self.test_speed_indices_pair(max_speeds,
                               arc_lengths, previous_speed_index, speed_index)
        is_compatible_with_next = self.test_speed_indices_pair(max_speeds, 
                               arc_lengths, speed_index, next_speed_index)
        is_speed_index_compatible = (is_compatible_with_previous and
                                         is_compatible_with_next)
        return [is_speed_index_compatible, position_of_speed_index]

    def add_compatible_speed_to_profile(self, max_speeds, arc_lengths):
        for i in xrange(len(self.sorted_interior_max_speeds_indices)):
            speed_index = self.sorted_interior_max_speeds_indices[i]
            is_speed_index_compatible, position_of_speed_index = \
                self.test_speed_index(speed_index, max_speeds, arc_lengths)
            if is_speed_index_compatible:
                self.sorted_interior_max_speeds_indices.pop(i)
                self.selected_max_speeds_indices = np.insert(
                            self.selected_max_speeds_indices,
                        position_of_speed_index, speed_index)
                return True
        return False

    def get_speed_profile_waypoints(self, max_speeds, arc_lengths):
        self.selected_max_speeds_indices = []
        start_speed_index = 0
        self.selected_max_speeds_indices.append(start_speed_index)
        final_speed_index = len(max_speeds) - 1
        self.selected_max_speeds_indices.append(final_speed_index)
        interior_max_speeds = max_speeds[1: final_speed_index]
        self.sorted_interior_max_speeds_indices = \
            self.sort_speeds_indices(interior_max_speeds)
        self.index_pairs_tested = [[0 for i in range(len(max_speeds))]
                                      for j in range(len(max_speeds))]
        while True:
            added_compatible_speed = \
                self.add_compatible_speed_to_profile(max_speeds, arc_lengths)
            if added_compatible_speed:
                pass
            else:
                break
        waypoint_arc_lengths = [arc_lengths[index] for index
                                in self.selected_max_speeds_indices]
        waypoint_max_speeds = [max_speeds[index] for index
                               in self.selected_max_speeds_indices]
        return [waypoint_arc_lengths, waypoint_max_speeds]
        
    def interpolate_speed_waypoints(self, waypoint_arc_lengths,
                                          waypoint_max_speeds):
        speed_spline = scipy.interpolate.PchipInterpolator(
                        waypoint_arc_lengths, waypoint_max_speeds)
        return speed_spline
            
    def build_speeds_by_arc_length(self, arc_lengths, max_speeds):
        waypoint_arc_lengths, waypoint_speeds = \
            self.get_speed_profile_waypoints(max_speeds, arc_lengths)
        speed_spline = self.interpolate_speed_waypoints(waypoint_arc_lengths, 
                                                             waypoint_speeds)   
        speeds_by_arc_length = speed_spline(arc_lengths)
        return speeds_by_arc_length

    def reparametrize_speed(self, arc_lengths, speeds_by_arc_length):
        times_by_arc_length = \
            reparametrize_speed.speeds_by_arc_length_to_times_by_arc_length(
                                          speeds_by_arc_length, arc_lengths)        
        speeds_by_time, cumulative_time_steps = \
            reparametrize_speed.speeds_by_arc_length_to_speeds_by_time(
                speeds_by_arc_length, arc_lengths, self.TIME_STEP_SIZE)
        return [times_by_arc_length, cumulative_time_steps, speeds_by_time]
    
    def __init__(self, spatial_path_3d,
                 max_longitudinal_accel=None, jerk_tol=None):
        if max_longitudinal_accel == None:
            self.max_longitudinal_accel = parameters.MAX_LONGITUDINAL_ACCEL
        else:
            self.max_longitudinal_accel = max_longitudinal_accel

        if jerk_tol == None:
            self.jerk_tol = parameters.JERK_TOL
        else:
            self.jerk_tol = jerk_tol

        arc_lengths = spatial_path_3d.arc_lengths
        max_speeds = spatial_path_3d.max_allowed_speeds
        max_speeds[0] = max_speeds[-1] = 0.0
        speeds_by_arc_length = self.build_speeds_by_arc_length(arc_lengths, 
                                                                max_speeds)
        times_by_arc_length, cumulative_time_steps, speeds_by_time = \
            self.reparametrize_speed(arc_lengths, speeds_by_arc_length)      
        trip_time = times_by_arc_length[-1]
        self.times_by_arc_length = times_by_arc_length
        self.speeds_by_arc_length = speeds_by_arc_length
        self.trip_time = trip_time
        self.cumulative_time_steps = cumulative_time_steps
        self.speeds_by_time = speeds_by_time
        self.accels_by_time = [] #accels_by_time
