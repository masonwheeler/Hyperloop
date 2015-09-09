"""
Original Developer: Jonathan Ward
Purpose of Module: To build a lattice using smoothing spline.
Last Modified: 8/13/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added Iteratively Spline construction
"""

# Standard Modules:
import numpy as np
import time

# Our Modules:
import abstract_lattice as abstract
import cacher
import config
import curvature
import interpolate
import parameters
import proj
import util


class SpatialPoint(abstract.AbstractPoint):

    def __init__(self, point_id, lattice_x_coord, lattice_y_coord,
                                  geospatial, is_in_right_of_way):
        spatial_x_coord, spatial_y_coord = geospatial
        abstract.AbstractPoint.__init__(self, point_id, lattice_x_coord,
                             lattice_y_coord, spatial_x_coord, spatial_y_coord)
        self.geospatial = geospatial
        self.latlng = proj.geospatial_to_latlng(geospatial, config.PROJ)
        self.is_in_right_of_way = is_in_right_of_way


class SpatialSlice(abstract.AbstractSlice):

    @staticmethod
    def spatial_slice_points_builder(lattice_x_coord, spatial_slice_bounds,
                                                     slice_start_id):
        spatial_slice_y_spacing = spatial_slice_bounds["y_spacing"]
        spline_geospatials = spatial_slice_bounds["spline_geospatials"]
        directions_geospatials = spatial_slice_bounds["directions_geospatials"]
        spatial_slice_geospatials, distances = util.build_grid(
                                            directions_geospatials,
                                            spline_geospatials,
                                            spatial_slice_y_spacing)
        point_id = slice_start_id
        lattice_y_coord = 0
        spatial_slice_points = []
        for spatial_slice_geospatial in spatial_slice_geospatials: #[:-1]:
            is_in_right_of_way = (lattice_y_coord == 0)
            new_spatial_point = SpatialPoint(point_id, lattice_x_coord,
                lattice_y_coord, spatial_slice_geospatial, is_in_right_of_way)
            spatial_slice_points.append(new_spatial_point)
            point_id += 1
            lattice_y_coord += 1        
        return [spatial_slice_points, point_id]        

    def __init__(self, lattice_x_coord, spatial_slice_bounds, slice_start_id):
        abstract.AbstractSlice.__init__(self, lattice_x_coord,
                                        spatial_slice_bounds, slice_start_id,
                                    SpatialSlice.spatial_slice_points_builder)


class SpatialLattice(abstract.AbstractLattice):
    SMOOTHING_SPATIAL_SPLINE_INITIAL_END_WEIGHTS = 10**5
    SMOOTHING_SPATIAL_SPLINE_INITIAL_SMOOTHING_FACTOR = 10**13
    BASE_RESOLUTION = 10 #Meters
    
    def get_spatial_splines(self, sampled_directions_geospatials):
        geospatials_x_values = [geospatial[0] for geospatial
                                in sampled_directions_geospatials]
        geospatials_y_values = [geospatial[1] for geospatial
                                in sampled_directions_geospatials]
        x_array = np.array(geospatials_x_values)
        y_array = np.array(geospatials_y_values)
        initial_end_weights = \
            self.SMOOTHING_SPATIAL_SPLINE_INITIAL_END_WEIGHTS
        initial_smoothing_factor = \
            self.SMOOTHING_SPATIAL_SPLINE_INITIAL_SMOOTHING_FACTOR
        curvature_threshold = curvature.compute_curvature_threshold(
                 parameters.MAX_SPEED, parameters.MAX_LATERAL_ACCEL)
        x_spline, y_spline = interpolate.iterative_smoothing_interpolation_2d(
                                                                      x_array,
                                                                      y_array,
                                                          initial_end_weights,
                                                     initial_smoothing_factor,
                                                          curvature_threshold)
        return [x_spline, y_spline]
    
    def sample_directions_geospatials(self, directions_geospatials):
        sampled_directions_geospatials = interpolate.sample_path(
                        directions_geospatials, self.BASE_RESOLUTION)
        return sampled_directions_geospatials
   
    @staticmethod
    def get_spatial_slices_directions_geospatials(
            sampled_directions_geospatials, spatial_x_spacing):
        spatial_slices_directions_geospatials = util.smart_sample_nth_points(
            sampled_directions_geospatials, spatial_x_spacing)
        return spatial_slices_directions_geospatials
    
    def get_spatial_slices_spline_geospatials(self,
            sampled_directions_geospatials, spatial_x_spacing): 
        self.spatial_spline_s_values = interpolate.get_s_values(len(
                                        sampled_directions_geospatials))
        spatial_slices_s_values = interpolate.get_slice_s_values(
            self.spatial_spline_s_values, spatial_x_spacing)
        self.spatial_x_spline, self.spatial_y_spline = self.get_spatial_splines(
                                               sampled_directions_geospatials)
        spatial_slices_spline_points_x_values = interpolate.get_spline_values(
                          self.spatial_x_spline, spatial_slices_s_values)
        spatial_slices_spline_points_y_values = interpolate.get_spline_values(
                          self.spatial_y_spline, spatial_slices_s_values)
        spatial_slices_spline_tuples = zip(
            spatial_slices_spline_points_x_values,
            spatial_slices_spline_points_y_values)
        spatial_slices_spline_points = [list(eachTuple) for eachTuple in
                                            spatial_slices_spline_tuples]
        return spatial_slices_spline_points
    
    def get_spatial_slices_bounds(self, spatial_slices_directions_points,
                                  spatial_slices_spline_points,
                                  spatial_y_spacing):
        spatial_slices_bounds = []
        for i in range(len(spatial_slices_directions_points)):
            spatial_slice_bounds = {"directions_geospatials":  
                                    spatial_slices_directions_points[i],
                                    "spline_geospatials":
                                    spatial_slices_spline_points[i],
                                    "y_spacing":
                                    spatial_y_spacing}
            spatial_slices_bounds.append(spatial_slice_bounds)
        return spatial_slices_bounds        

    def __init__(self, directions, spatial_x_spacing_power,
                                              spatial_y_spacing_power): 
        self.start_latlng = directions.start_latlng
        self.end_latlng = directions.end_latlng
        self.projection = directions.projection
        self.directions_geospatials = directions.geospatials
        directions_s_value_step_size = 2**spatial_x_spacing_power
        self.spatial_x_spacing = 2**spatial_x_spacing_power * \
                                 self.BASE_RESOLUTION
        self.spatial_y_spacing = 2**spatial_y_spacing_power * \
                                 self.BASE_RESOLUTION
        sampled_directions_geospatials = self.sample_directions_geospatials(
                                                self.directions_geospatials)
        spatial_slices_directions_geospatials = \
            SpatialLattice.get_spatial_slices_directions_geospatials(
                   sampled_directions_geospatials, directions_s_value_step_size)
        spatial_slices_spline_geospatials = \
            self.get_spatial_slices_spline_geospatials(
            sampled_directions_geospatials, directions_s_value_step_size)
        spatial_slices_bounds = self.get_spatial_slices_bounds(
                                    spatial_slices_directions_geospatials,
                                    spatial_slices_spline_geospatials,
                                    self.spatial_y_spacing)
        abstract.AbstractLattice.__init__(self, spatial_slices_bounds,
                                                         SpatialSlice)

    def get_plottable_directions(self):
        x_values = [geospatial[0] for geospatial in self.directions_geospatials]
        y_values = [geospatial[1] for geospatial in self.directions_geospatials]
        x_array = np.array(x_values)
        y_array = np.array(y_values)
        return [x_array, y_array]    

    def get_plottable_spline(self):
        x_values = self.spatial_x_spline(self.spatial_spline_s_values)
        y_values = self.spatial_y_spline(self.spatial_spline_s_values)
        x_array = np.array(x_values)
        y_array = np.array(y_values)
        return [x_array, y_array]
        
            
def get_spatial_lattice(directions, spatial_x_spacing, spatial_y_spacing):
    lattice = cacher.get_object("spatial_lattice", SpatialLattice,
                 [directions, spatial_x_spacing, spatial_y_spacing],
                 config.SPATIAL_LATTICE_FLAG)    
    return lattice
