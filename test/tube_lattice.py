"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import abstract_lattice
import config
import parameters
import util
import visualize


class TubePoint(abstract_lattice.AbstractPoint):

    def compute_pylon_cost(self):
        if self.is_undeground:
            pylon_cost = 0
        else:
            height_cost = (self.pylon_height * 
                           parameters.PYLON_COST_PER_METER)
            base_cost = parameters.PYLON_BASE_COST
            pylon_cost = height_cost + base_cost
        return pylon_cost

    def build_pylon_at_tube_point(self):
        pylon_at_tube_point = {"height": self.pylon_height,
                               "cost": self.pylon_cost,
                               "latlng": self.latlng}
        return pylon_at_tube_point

    def __init__(self, point_id, abstract_x_coord, abstract_y_coord, arc_length,
                       geospatial, latlng, tube_elevation, land_elevation):
        self.arc_length = arc_length
        self.latlng = latlng
        self.geospatial = geospatial
        self.land_elevation = land_elevation
        self.tube_elevtion = tube_elevation
        self.pylon_height = tube_elevation - land_elevation
        self.pylon_cost = self.compute_pylon_cost()
        self.physical_x_coord = distance_along_path
        self.physical_y_coord = tube_elevation
        abstract_lattice.AbstractPoint.__init__(self, point_id, abstract_x_coord,
                  abstract_y_coord, self.physical_x_coord, self.physical_y_coord)


class TubePointsSlice(abstract_lattice.AbstractSlice):

    @staticmethod
    def tube_points_slice_builder(abstract_x_coord, tube_points_slice_bounds,
                                                        slice_start_point_id):
        tube_elevation_step_size = tube_points_slice_bounds["elevationStepSize"]
        min_tube_elevation = tube_points_slice_bounds["minTubeElevation"]
        max_tube_elevation = tube_points_slice_bounds["maxTubeElevation"]
        arc_length = tube_points_slice_bounds["arcLength"]
        geospatial = tube_points_slice_bounds["geospatial"]
        latlng = tube_points_slice_bounds["latlng"]
        land_elevation = tube_points_slice_bounds["landElevation"]

        tube_elevations = util.build_grid_1d(max_tube_elevation,
            min_tube_elevation, tube_elevation_step_size)
        point_id = slice_start_point_id
        abstract_y_coord = 0
        tube_points = []
        for tube_elevation in tube_elevations:
            tube_point = TubePoint(point_id,
                                   abstract_x_coord,
                                   abstract_y_coord,
                                   arc_length,
                                   geospatial,
                                   latlng,
                                   tube_elevation,
                                   land_elevation)
            tube_points.append(tube_point)
            point_id += 1
            abstract_y_coord += 1
        return [tube_points, point_id]

    def __init__(self, abstract_x_coord, tube_points_slice_bounds,
                                             slice_start_point_id):
        abstract_lattice.AbstractSlice.__init__(self, abstract_x_coord,
                              tube_points_slice_bounds, slice_start_id,
                             TubePointsSlice.tube_points_slice_builder)


class TubePointsLattice(abstract_lattice.AbstractLattice):

    def build_lower_tube_envelope_v1(self, elevation_profile):
        first_land_elevation = elevation_profile.land_elevations[0]
        last_land_elevation = elevation_profile.land_elevations[-1]
        land_elevation_difference = last_land_elevation - first_land_elevation
        first_arc_length = elevation_profile.arc_lengths[0]
        last_arc_length = elevation_profile.arc_lengths[-1]
        arc_length_difference = last_arc_length - first_arc_length
        lower_tube_envelope = []
        for arc_length in elevation_profile.arc_lengths[0]:
            lower_tube_envelope_point = (land_elevation_difference * 
                ((arc_length - first_arc_length) / arc_length_difference))
            lower_tube_envelope.append(lower_tube_envelope_point)
        return lower_tube_envelope

    def build_lower_tube_envelope_v2(self, elevation_profile):
        lowest_land_elevation = min(elevation_profile.land_elevations)
        lower_tube_envelope = ([lowest_land_elevation] *
                               len(elevation_profile.land_elevations))
        return lower_tube_envelope

    def build_upper_tube_envelope(self, elevation_profile):
        land_elevation_peaks_indices = scipy(elevation_profile.land_elevations)
        num_envelope_points = len(elevation_profile.land_elevations)
        weights = np.arange(num_envelope_points)
        peaks_weights = 100
        remaining_weights = 1
        for i in range(num_envelope_points):
            if i in land_elevation_peaks_indices:
                weights[i] = peaks_weights
            else:
                weights[i] = remaining_weights
        upper_tube_envelope = interpolate_peaks(elevation_profile, weights)        
        return upper_tube_envelope
       
    def tube_envelopes_to_tube_slice_bounds(self, lower_tube_envelope,
          upper_tube_envelope, elevation_profile, elevation_step_size):
        tube_points_slices_bounds = []
        for i in range(len(elevation_profile.arc_lengths)):
            tube_points_slice_bounds = {
                "elevationStepSize" : elevation_step_size,
                "minTubeElevation" : lower_tube_envelope[i],
                "maxTubeElevation" : upper_tube_envelope[i],
                "arcLength" : elevation_profile.arc_lengths[i],
                "geospatial" : elevation_profile.geospatials[i],
                "latlng" : elevation_profile.latlngs[i],
                "landElevation" : elevation_profile.land_elevation[i]
                }
            tube_points_slices_bounds.append(tube_points_slice_bounds) 
        return tube_points_slices_bounds

    def __init__(self, elevation_profile, elevation_step_size):
        lower_tube_enevelope = self.build_lower_tube_envelope(elevation_profile)
        upper_tube_enevelope = self.build_upper_tube_envelope(elevation_profile)
        tube_points_slices_bounds = tube_envelopes_to_tube_slice_bounds(
            lower_tube_envelope, upper_tube_envelope, elevation_profile,
                                                    elevation_step_size)
        abstract_lattice.AbstractLattice.__init__(self,
                             tube_points_slices_bounds,
             TubePointsSlice.tube_points_slice_builder)

