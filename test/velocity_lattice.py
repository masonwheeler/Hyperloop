"""
Original Developer: Jonathan Ward.
"""

class Velocity(abstract.AbstractPoint):

    def __init__(self, speed, distance_along_path, velocity_id):
        velocity_coords = {"speed": speed,
                           "distance_along_path":  distance_along_path}
        abstract.AbstractPoint.__init__(velocity_coords, velocity_id)


class VelocitiesSlice(abstract.AbstractSlice):

    def velocities_builder(self, velocities_slice_bounds, lowest_velocity_id):
        max_speed = velocities_slice_bounds["max_speed"]
        min_speed = velocities_slice_bounds["min_speed"]
        speed_step_size = velocities_slice_bounds["speed_step_size"]
        speed_difference = max_speed - min_speed
        speed_options = util.build_grid2(speed_difference,
                                         speeds_step_size, minimum_speed)
        velocity_ids = [index + lowest_velocity_id for index
                        in range(len(speed_options))]
        velocity_options = [Velocity(speed_options[i], distance_along_path,
                                     velocity_ids[i]) for i in range(len(velocity_ids))]
        return velocity_options

    def __init__(self, velocities_slice_bounds, lowest_velocity_id):
        abstract.AbstractSlice.__init__(velocities_slice_bounds,
                                        lowest_velocity_id, self.velocities_builder)

class VelocitiesLattice(abstract.AbstractLattice):

    def max_allowed_velocities_to_velocity_slice_bounds(max_allowed_velocities):
        num_arc_length_steps = max_allowed_velocities.length - 1
        arc_length_steps_array = np.empty(num_arc_length_points)
        arc_length_steps_array = np.fill(config.ARCLENGTH_STEP_SIZE)
        partial_arc_length_array = np.cumsum(arc_length_steps_array)
        arc_length_array = np.insert(partial_arc_length_array, 0, 0)
        velocity_slices_bounds = []
        for i in range(len(max_allowed_velocities.length)):
            max_speed = max_allowed_velocities[i]
            min_speed = config.SPEED_STEP_SIZE
            speed_step_size = config.SPEED_STEP_SIZE
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

