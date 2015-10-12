"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import numpy as np
import scipy.signal

# Custom Modules:
import abstract_lattice
import config
import smoothing_interpolate
import parameters
import util


class TubePoint(abstract_lattice.AbstractPoint):

    def compute_pylon_cost(self):
        if self.is_underground:
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
        self.tube_elevation = tube_elevation
        self.pylon_height = tube_elevation - land_elevation
        self.is_underground = (self.pylon_height < 0)     
        self.pylon_cost = self.compute_pylon_cost()
        self.physical_x_coord = arc_length
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
        tube_elevations = util.build_grid_1d(min_tube_elevation,
            max_tube_elevation, tube_elevation_step_size)
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
                        tube_points_slice_bounds, slice_start_point_id,
                             TubePointsSlice.tube_points_slice_builder)


class TubePointsLattice(abstract_lattice.AbstractLattice):

    BASE_ELEVATION_STEP_SIZE = 1.0 #Meter

    def build_lower_tube_envelope(self, arc_lengths, land_elevations):
        land_elevation_troughs_indices_tuple = scipy.signal.argrelmin(
                                                 land_elevations, order=10)
        land_elevation_troughs_indices = \
            land_elevation_troughs_indices_tuple[0].tolist()
        lower_tube_envelope = \
            smoothing_interpolate.bounded_curvature_extrema_interpolate(
            arc_lengths, land_elevations, land_elevation_troughs_indices, 
            parameters.MAX_VERTICAL_CURVATURE)
        return lower_tube_envelope

    def build_upper_tube_envelope(self, arc_lengths, land_elevations):
        land_elevation_peaks_indices_tuple = scipy.signal.argrelmax(
                                               land_elevations, order=10)
        land_elevation_peaks_indices = \
            land_elevation_peaks_indices_tuple[0].tolist()
        upper_tube_envelope = \
            smoothing_interpolate.bounded_curvature_extrema_interpolate(
             arc_lengths, land_elevations, land_elevation_peaks_indices,
                                      parameters.MAX_VERTICAL_CURVATURE)
        return upper_tube_envelope

    def sampled_tube_envelopes_to_tube_slice_bounds(self, 
            sampled_lower_tube_envelope, sampled_upper_tube_envelope, 
            sampled_elevation_profile, elevation_step_size):
        tube_points_slices_bounds = []
        for i in range(len(sampled_elevation_profile.arc_lengths)):
            tube_points_slice_bounds = {
                "elevationStepSize" : elevation_step_size,
                "minTubeElevation" : sampled_lower_tube_envelope[i],
                "maxTubeElevation" : sampled_upper_tube_envelope[i],
                "arcLength" : sampled_elevation_profile.arc_lengths[i],
                "geospatial" : sampled_elevation_profile.geospatials[i],
                "latlng" : sampled_elevation_profile.latlngs[i],
                "landElevation" : sampled_elevation_profile.land_elevations[i]
                }
            tube_points_slices_bounds.append(tube_points_slice_bounds) 
        return tube_points_slices_bounds

    def __init__(self, elevation_profile, elevation_mesh_bisection_depth,
                                         arc_length_mesh_bisection_depth):
        elevation_step_size = (self.BASE_ELEVATION_STEP_SIZE *
                               2**elevation_mesh_bisection_depth)
        self.arc_lengths = elevation_profile.arc_lengths
        self.land_elevations = elevation_profile.land_elevations
        self.lower_tube_envelope = self.build_lower_tube_envelope(
            self.arc_lengths, self.land_elevations)
        self.upper_tube_envelope = self.build_upper_tube_envelope(
            self.arc_lengths, self.land_elevations)

        undersampling_factor = 2**arc_length_mesh_bisection_depth
        sampled_lower_tube_envelope = self.lower_tube_envelope[::
                                                 undersampling_factor]
        sampled_upper_tube_envelope = self.upper_tube_envelope[::
                                                 undersampling_factor]
        sampled_elevation_profile = elevation_profile.undersample(
                                                 undersampling_factor)
        tube_points_slices_bounds = \
            self.sampled_tube_envelopes_to_tube_slice_bounds(
                    sampled_lower_tube_envelope, sampled_upper_tube_envelope,
                              sampled_elevation_profile, elevation_step_size)
        abstract_lattice.AbstractLattice.__init__(self,
            tube_points_slices_bounds, TubePointsSlice)
        self.resolution = elevation_step_size
        self.length_scale = elevation_profile.arc_length_step_size


