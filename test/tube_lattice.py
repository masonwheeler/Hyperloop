"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import abstract_lattice
import parameters
import pylon_cost
import util

class PylonPoint(abstract_lattice.AbstractPoint):

    def __init__(self, pylon_id, abstract_x_coord, abstract_y_coord, arc_length,
                       geospatial, latlng, land_elevation, pylon_height):
        self.pylon_height = pylon_height
        self.land_elevation = land_elevation
        self.latlng = latlng
        tube_elevation = land_elevation + pylon_height
        x_value, y_value = geospatial
        z_value = tube_elevation
        self.tube_coords = [x_value, y_value, z_value]
        self.pylon_cost = pylon_cost.compute_pylon_cost_v1(pylon_height)
        self.spatial_x_coord = distance_along_path
        self.spatial_y_coord = tube_elevation
        abstract_lattice.AbstractPoint.__init__(self, pylon_id, lattice_x_coord,
                    lattice_y_coord, self.spatial_x_coord, self.spatial_y_coord)


class PylonsSlice(abstract_lattice.AbstractSlice):

    @staticmethod
    def pylons_slice_points_builder(abstract_x_coord, pylon_slice_bounds,
                                                  slice_start_id):
        pylon_height_step_size = pylon_slice_bounds["heightStepSize"]
        max_height = pylon_slice_bounds["maxHeight"]
        arc_length = pylon_slice_bounds["arcLength"]
        geospatial = pylon_slice_bounds["geospatial"]
        latlng = pylon_slice_bounds["latlng"]
        land_elevation = pylon_slice_bounds["land_elevation"]

        min_height = 0
        pylon_heights = util.build_grid_1d(max_height, min_height,
                                                  pylon_height_step_size)
        point_id = slice_start_id
        abstract_y_coord = 0
        pylons_slice_points = []
        for pylon_height in pylon_heights:
            new_pylon_point = PylonPoint(point_id,
                                         abstract_x_coord,
                                         abstract_y_coord,
                                         arc_length,
                                         geospatial
                                         latlng,
                                         land_elevation
                                         pylon_height)
            pylons_slice_points.append(new_pylon_point)
            point_id += 1
            abstract_y_coord += 1
        return [pylons_slice_points, point_id]

    def __init__(self, abstract_x_coord, pylon_slice_bounds, slice_start_id):
        abstract_lattice.AbstractSlice.__init__(self, abstract_x_coord,
                                    pylon_slice_bounds, slice_start_id,
                                 PylonSlice.pylon_slice_points_builder)


class PylonsLattice(abstract_lattice.AbstractLattice):

    def circle_function(self, x, r):
        if x > r:
            return -float("Inf")
        else:
            y = np.sqrt(np.square(r) - np.square(x)) - r
            return y

    def build_window(self, left_bound, right_bound, radius):
        relative_indices = range(-left_bound, right_bound + 1)
        window = [{"relative_index": relative_index,
                   "relative_elevation": self.circle_function(
                       abs(relative_index * parameters.PYLON_SPACING), radius)}
                  for relative_index in relative_indices]
        return window

    def add_current_window(self, envelope, current_window):
        for point in current_window:
            current_index = point["index"]
            envelope[current_index].append(point["elevation"])

    def build_envelope(self, elevations, radius):
        window_size = int(radius / config.PYLON_SPACING)
        envelope_lists = [[] for i in xrange(len(elevations))]
        for current_index in range(0, len(elevations)):
            if current_index < window_size:
                left_bound = current_index
            else:
                left_bound = window_size
            if current_index > (len(elevations) - 1) - window_size:
                right_bound = (len(elevations) - 1) - current_index
            else:
                right_bound = window_size
            relative_window = self.build_window(
                left_bound, right_bound, radius)
            current_elevation = elevations[current_index]
            current_window = [{
                "index": point["relative_index"] + current_index,
                "elevation": point["relative_elevation"] + current_elevation}
                for point in relative_window]
            self.add_current_window(envelope_lists, current_window)
        envelope = map(max, envelope_lists)
        return envelope

   def build_pylons_envelopes(self, elevation_profile):
        distances = []
        elevations = []
        for elevation_point in elevation_profile:
            distances.append(elevation_point["distance_along_path"])
            elevations.append(elevation_point["land_elevation"])
        max_speed = parameters.MAX_SPEED
        curvature_threshold_upper = interpolate.compute_curvature_threshold(
            max_speed, parameters.MAX_VERTICAL_ACCEL)
        radius_upper = 1.0 / curvature_threshold_upper
        envelope_upper = self.build_envelope(elevations, radius_upper)
        min_speed = parameters.MIN_SPEED
        curvature_threshold_lower = interpolate.compute_curvature_threshold(
            min_speed, paramters.MAX_VERTICAL_ACCEL)
        radius_lower = 1.0 / curvature_threshold_lower
        envelope_lower = self.build_envelope(elevations, radius_lower)
        return [envelope_upper, envelope_lower]

    def envelope_point_to_bounds(self, data_point):
        elevation_point, envelope_point_upper, envelope_point_lower = data_point
        land_elevation = elevation_point["land_elevation"]
        pylons_slice_bounds = {
            "tallest_pylon_height": envelope_point_upper - land_elevation,
            "shortest_pylon_height": envelope_point_lower - land_elevation,
            "distance_along_path": elevation_point["distance_along_path"],
            "geospatial": elevation_point["geospatial"],
            "latlng": elevation_point["latlng"],
            "land_elevation": land_elevation,
            "pylon_height_step_size": parameters.PYLON_HEIGHT_STEP_SIZE
        }
        return pylons_slice_bounds

    def build_pylons_slices_bounds(self, elevation_profile, pylons_envelope_upper,
                                   pylons_envelope_lower):
        pylons_data = zip(elevation_profile, pylons_envelope_upper,
                          pylons_envelope_lower)
        pylons_slices_bounds = [self.envelope_point_to_bounds(data_point)
                                for data_point in pylons_data]
        return pylons_slices_bounds

    def __init__(self, elevation_profile):
        pylons_envelope_upper, pylons_envelope_lower = \
            self.build_pylons_envelopes(elevation_profile)
        pylons_slices_bounds = self.build_pylons_slices_bounds(
            elevation_profile, pylons_envelope_upper, pylons_envelope_lower)
        abstract_lattice.AbstractLattice.__init__(self, pylons_slices_bounds,
                                      PylonsSlice.pylon_slice_points_builder)

