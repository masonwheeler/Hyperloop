"""
Original Developer: Jonathan Ward
Purpose of Module: To build a lattice using smoothing spline.
Last Modified: 8/13/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added Iteratively Spline construction
"""

# Standard Modules:
import numpy as np

# Our Modules:
import abstract_lattice
import cacher
import parameters
import sample_path
import smoothing_interpolate
import util


class SpatialPoint(abstract_lattice.AbstractPoint):

    def __init__(self, point_id, abstract_x_coord, abstract_y_coord,
                                  geospatial, is_in_right_of_way):
        physical_x_coord, physical_y_coord = geospatial
        abstract_lattice.AbstractPoint.__init__(self, point_id,
                            abstract_x_coord, abstract_y_coord,
                            physical_x_coord, physical_y_coord)
        self.geospatial = geospatial
        self.is_in_right_of_way = is_in_right_of_way


class SpatialSlice(abstract_lattice.AbstractSlice):

    @staticmethod
    def spatial_slice_points_builder(abstract_x_coord, spatial_slice_bounds,
                                                             slice_start_id):
        spatial_slice_y_spacing = spatial_slice_bounds["ySpacing"]
        spline_geospatials = spatial_slice_bounds["splineGeospatials"]
        directions_geospatials = spatial_slice_bounds["directionsGeospatials"]
        spatial_slice_geospatials, distances = util.build_grid(
                                            spline_geospatials,
                                            directions_geospatials,
                                            spatial_slice_y_spacing)
        point_id = slice_start_id
        abstract_y_coord = 0
        spatial_slice_points = []
        for spatial_slice_geospatial in spatial_slice_geospatials:
            is_in_right_of_way = (abstract_y_coord == 0)
            new_spatial_point = SpatialPoint(point_id, abstract_x_coord,
                abstract_y_coord, spatial_slice_geospatial, is_in_right_of_way)
            spatial_slice_points.append(new_spatial_point)
            point_id += 1
            abstract_y_coord += 1        
        return [spatial_slice_points, point_id]        

    def __init__(self, abstract_x_coord, spatial_slice_bounds, slice_start_id):
        abstract_lattice.AbstractSlice.__init__(self, abstract_x_coord,
                                  spatial_slice_bounds, slice_start_id,
                             SpatialSlice.spatial_slice_points_builder)


class SpatialLattice(abstract_lattice.AbstractLattice):
    SPATIAL_SPLINE_END_WEIGHTS = 10**5
    SPATIAL_SPLINE_SMOOTHING_FACTOR = 10**13
    SPATIAL_BASE_RESOLUTION = 100 #Meters
    
    NAME = "spatial_lattice"
    FLAG = cacher.SPATIAL_LATTICE_FLAG
    IS_SKIPPED = cacher.SKIP_LATTICE

    def get_splines(self, sampled_directions_geospatials):
        x_array, y_array = np.transpose(sampled_directions_geospatials)
        weights = np.empty(sampled_directions_geospatials.shape[0])
        weights.fill(1)
        weights[0] = weights[-1] = self.SPATIAL_SPLINE_END_WEIGHTS
        smoothing_factor = self.SPATIAL_SPLINE_SMOOTHING_FACTOR
        max_curvature = parameters.MAX_LATERAL_CURVATURE
        x_spline, y_spline = \
            smoothing_interpolate.iterative_smoothing_interpolation_2d(
            x_array, y_array, weights, smoothing_factor, max_curvature)
        return [x_spline, y_spline]
    
    def sample_directions_geospatials(self, directions_geospatials):
        sampled_directions_geospatials, arc_lengths = \
          sample_path.sample_path_points(directions_geospatials,
                                         self.SPATIAL_BASE_RESOLUTION)
        return sampled_directions_geospatials
   
    def get_slices_directions_geospatials(self, sampled_directions_geospatials,
                                                  parallel_resolution_multiple):
        last_directions_geospatial = sampled_directions_geospatials[-1]
        slices_directions_geospatials = sampled_directions_geospatials[::
                                             parallel_resolution_multiple]
        slices_directions_geospatials = np.append(slices_directions_geospatials,
                                                    last_directions_geospatial)
        return slices_directions_geospatials
    
    def get_slices_spline_geospatials(self, sampled_directions_geospatials,
                                              parallel_resolution_multiple): 
        spline_s_values = np.arange(sampled_directions_geospatials.shape[0])
        slices_s_values = spline_s_values[::parallel_resolution_multiple]
        slices_s_values = np.append(slices_s_values, spline_s_values[-1])
        x_spline, y_spline = self.get_splines(sampled_directions_geospatials)
        slices_spline_x_values = x_spline(slices_s_values)
        slices_spline_y_values = y_spline(slices_s_values)
        slices_spline_geospatials = np.transpose([slices_spline_x_values,
                                                  slices_spline_y_values])
        return slices_spline_geospatials
    
    def get_spatial_slices_bounds(self, slices_directions_geospatials,
                     slices_spline_geospatials, transverse_resolution):
        spatial_slices_bounds = []
        for i in range(slices_directions_geospatials.shape[0]):
            spatial_slice_bounds = {"directionsGeospatials":  
                                    slices_directions_geospatials[i],
                                    "splineGeospatials":
                                    slices_spline_geospatials[i],
                                    "ySpacing":
                                    transverse_resolution
                                    }
            spatial_slices_bounds.append(spatial_slice_bounds)
        return spatial_slices_bounds        

    def __init__(self, directions, parallel_resolution_bisection_depth,
                                 transverse_resolution_bisection_depth):
        self.spatial_metadata = directions.spatial_metadata
        self.geospatials_to_latlngs = directions.geospatials_to_latlngs
        self.directions_geospatials = directions.geospatials

        parallel_resolution_multiple = 2**parallel_resolution_bisection_depth
        transverse_resolution_multiple = \
                                       2**transverse_resolution_bisection_depth
        self.parallel_resolution = (parallel_resolution_multiple *
                                    self.SPATIAL_BASE_RESOLUTION)
        self.transverse_resolution = (transverse_resolution_multiple *
                                      self.SPATIAL_BASE_RESOLUTION)

        sampled_directions_geospatials = self.sample_directions_geospatials(
                                                self.directions_geospatials)
        slices_directions_geospatials = self.get_slices_directions_geospatials(
                  sampled_directions_geospatials, parallel_resolution_multiple)
        self.slices_spline_geospatials = self.get_slices_spline_geospatials(
                   sampled_directions_geospatials, parallel_resolution_multiple)

        spatial_slices_bounds = self.get_spatial_slices_bounds(
            slices_directions_geospatials, self.slices_spline_geospatials,
                                     self.transverse_resolution)

        abstract_lattice.AbstractLattice.__init__(self, spatial_slices_bounds,
                                                                 SpatialSlice)

    def get_plottable_directions(self, color_string):
        directions_points = np.transpose(self.directions_geospatials)
        plottable_directions = [directions_points, color_string]
        return plottable_directions

    def get_plottable_spline(self, color_string):
        spline_points = np.transpose(self.slices_spline_geospatials)
        plottable_spline = [spline_points, color_string]
        return plottable_spline

            
def get_spatial_lattice(*args):
    lattice = cacher.get_object(SpatialLattice.NAME,
                                SpatialLattice,
                                args,
                                SpatialLattice.FLAG,
                                SpatialLattice.IS_SKIPPED)
    return lattice
