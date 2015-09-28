"""
Original Developer: Jonathan Ward.
"""

import abstract_lattice
import parameters
import util

class SpeedPoint(abstract_lattice.AbstractPoint):

    def __init__(self, point_id, abstract_x_coord, abstract_y_coord, 
                                                  speed, arc_length):
        physical_x_coord = arc_length
        physical_y_coord = speed
        abstract_lattice.AbstractPoint.__init__(self, point_id,
                            abstract_x_coord, abstract_y_coord,
                            physical_x_coord, physical_y_coord)


class SpeedsSlice(abstract_lattice.AbstractSlice):

    @staticmethod
    def speeds_slice_points_builder(self, abstract_x_coord,
                             speeds_slice_bounds, slice_start_id):
        max_speed = speeds_slice_bounds["maxSpeed"]
        min_speed = speeds_slice_bounds["minSpeed"]
        arc_length = speeds_slice_bounds["arcLength"]
        speed_step_size = speeds_slice_bounds["speedStepSize"]
        speed_difference = max_speed - min_speed
        speed_options = util.build_grid_1d(max_speed, min_speed,
                                               speed_step_size)
        point_id = slice_start_id
        abstract_y_coord = 0
        speeds_slice_points = []
        for speed in speed_options:
            new_speed_point = SpeedPoint(point_id,
                                         abstract_x_coord,
                                         abstract_y_coord,
                                         speed,
                                         arc_length)
            speeds_slice_points.append(new_speed_point)
            point_id += 1
            abstract_y_coord += 1        
        return speeds_slice_points

    def __init__(self, abstract_x_coord, speeds_slice_bounds, slice_start_id):
        abstract_lattice.AbstractSlice.__init__(abstract_x_coord,
                             speeds_slice_bounds, slice_start_id,
                         SpeedsSlice.speeds_slice_points_builder)


class SpeedsLattice(abstract_lattice.AbstractLattice):


    def max_allowed_velocities_to_velocity_slice_bounds(
            max_allowed_velocities_by_arc_length, arc_lengths, speed_step_size):
        velocity_slices_bounds = []
        for i in range(len(max_allowed_velocities.length)):
            max_speed = max_allowed_velocities[i]
            min_speed = speed_step_size
            speed_step_size = paramete
            distance_along_path = arc_length_array[i]
            velocity_slice_bounds = {"max_speed": max_speed,
                                     "min_speed": min_speed,
                                     "speed_step_size": speed_step_size}
            velocity_slices_bounds.append(velocity_slice_bounds)
        return velocity_slices_bounds

    def __init__(self, max_allowed_velocities):
        velocity_slices_bounds = max_allowed_velocities_to_velocity_slice_bounds(
            max_allowed_velocities)
        abstract.AbstractLattice.__init__(velocities_slices_bounds,
                                          VelocitiesSlice)

