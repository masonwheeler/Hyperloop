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
import config
import util
import cacher
import proj
import interpolate


class SlicePoint:
    """Builds a point from geospatial coordinates, id, and a rightofway flag"""
    point_id = 0  # Unique identifier used in merging process.
    geospatial_coords = []
    latlng_coords = []
    # Denotes whether the point is on state property.
    is_in_right_of_way = False

    def __init__(self, point_id, geospatial_coords, is_in_right_of_way):
        self.point_id = point_id
        self.geospatial_coords = geospatial_coords
        self.is_in_right_of_way = is_in_right_of_way
        self.latlng_coords = proj.geospatial_to_latlng(geospatial_coords,
                                                       config.PROJ)

    def as_dict(self):
        """Returns the SlicePoint data as a dictionary"""
        point_dict = {"point_id": self.point_id,
                      "geospatial_coords": self.geospatial_coords,
                      "latlng_coords": self.latlng_coords,
                      "is_in_right_of_way": self.is_in_right_of_way}
        return point_dict


class Slice:
    """Builds Lattice Slice from a directions point and a spline point."""
    point_spacing = config.POINT_SPACING  # Sets the spacing between Slice points

    def build_slice(self, id_index, directions_point, spline_point):
        """Constructs each SlicePoint in the Slice and its id_index"""
        slice_grid, distances = util.build_grid(directions_point, spline_point,
                                                   self.point_spacing)       
        slice_grid_points = []
        for point in slice_grid[:-1]:
            slice_grid_points.append(SlicePoint(id_index, point,
                                                False).as_dict())
            id_index += 1
        slice_points = slice_grid_points
        return [slice_points, id_index]

    def __init__(self, id_index, directions_point, spline_point):
        self.slice_points, self.id_index = self.build_slice(id_index,
                                                            directions_point, spline_point)

    def as_list(self):
        return self.slice_points

    def plottable_slice(self):
        slice_geospatial_coords = [point["geospatial_coords"]
                                   for point in self.slice_points]
        plottable_slice = zip(*slice_geospatial_coords)
        return plottable_slice


class Lattice:
    """Builds Lattice from the directions, the splines and the arc-parameter"""
    lattice_slices = []
    plottable_slices = []

    def __init__(self, spatial_slice_bounds):
        slices = []
        id_index = 1
        for spatial_slice_bound in spatial_slice_bounds:
            directions_point, spline_point = spatial_slice_bound
            new_slice = Slice(id_index, directions_point, spline_point)
            id_index = new_slice.id_index
            self.lattice_slices.append(new_slice.as_list())


def build_lattice_slices(spatial_slice_bounds):
    lattice = Lattice(spatial_slice_bounds)
    lattice_slices = lattice.lattice_slices
    return lattice_slices


def curvature_test(x_spline, y_spline, s_values):
    splines_curvature = interpolate.parametric_splines_2d_curvature(
        x_spline, y_spline, s_values)
    is_curvature_valid = interpolate.is_curvature_valid(splines_curvature,
                                                        config.CURVATURE_THRESHHOLD)
    return is_curvature_valid


def iteratively_build_directions_spline(sampled_directions_points):
    x_coords_list, y_coords_list = zip(*sampled_directions_points)
    x_array, y_array = np.array(x_coords_list), np.array(y_coords_list)
    num_points = len(sampled_directions_points)
    s_values = np.arange(num_points)
    INITIAL_END_WEIGHTS = 100000
    INITIAL_SMOOTHING_FACTOR = 10**13
    x_spline, y_spline = interpolate.smoothing_splines_2d(x_array, y_array, s_values,
                                                          INITIAL_END_WEIGHTS, INITIAL_SMOOTHING_FACTOR)
    is_curvature_valid = curvature_test(x_spline, y_spline, s_values)
    if is_curvature_valid:
        test_smoothing_factor = INITIAL_SMOOTHING_FACTOR
        while is_curvature_valid:
            test_smoothing_factor *= 0.5
            interpolate.set_smoothing_factors_2d(x_spline, y_spline,
                                                 test_smoothing_factor)
            is_curvature_valid = curvature_test(x_spline, y_spline, s_values)
        test_smoothing_factor *= 2
        interpolate.set_smoothing_factors_2d(x_spline, y_spline,
                                             test_smoothing_factor)
        return [x_spline, y_spline]
    else:
        while not is_curvature_valid:
            test_smoothing_factor *= 2
            interpolate.set_smoothing_factors_2d(x_spline, y_spline,
                                                 test_smoothing_value)
            is_curvature_valid = curvature_test(x_spline, y_spline, s_values)
        return [x_spline, y_spline]


def get_directionsspline(sampled_directions_points):
    directions_spline = cacher.get_object("spline",
                                          iteratively_build_directions_spline,
                                          [sampled_directions_points],
                                          config.SPLINE_FLAG)
    return directions_spline


def get_lattice(spatial_slice_bounds):
    lattice = cacher.get_object("lattice", build_lattice_slices,
                                [spatial_slice_bounds], config.LATTICE_FLAG)
    return lattice


######### Spatial Lattice #########

class SpatialPoint(abstract.AbstractPoint):

    def __init__(self, point_id, lattice_x_coord, lattice_y_coord,
                                  geospatial, is_in_right_of_way):
        spatial_x_coord, spatial_y_coord = geospatial
        abstract.AbstractPoint.__init__(self, point_id, lattice_x_coord,
                             lattice_y_coord, spatial_x_coord, spatial_y_coord)
        self.latlng = proj.geospatial_to_latlng(geospatial, config.PROJ)
        self.is_in_right_of_way = is_in_right_of_way


class SpatialSlice(abstract.AbstractSlice):

    @staticmethod
    def spatial_slice_builder(lattice_x_coord, spatial_slice_bounds,
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
        for spatial_slice_geospatial in spatial_slice_geospatials[:-1]:
            is_in_right_of_way = (lattice_y_coord == 0)
            new_spatial_point = SpatialPoint(point_id, lattice_x_coord,
                lattice_y_coord, spatial_slice_geospatial, is_in_right_of_way)
            spatial_slice_points.append(new_spatial_points)
            point_id += 1
            lattice_y_coord += 1        
        return [spatial_slice_points, point_id]        

    def __init__(self, lattice_x_coord, spatial_slice_bounds, slice_start_id):
        abstract.AbstractSlice.__init__(self, lattice_x_coord,
                                        spatial_slice_bounds, slice_start_id,
                                        SpatialSlice.spatial_slice_builder)


class SpatialLattice(abstract.AbstractLattice):
    SMOOTHING_SPATIAL_SPLINE_INITIAL_END_WEIGHTS = 10**5
    SMOOTHING_SPATIAL_SPlINE_INITIAL_SMOOTHING_FACTOR = 10**13
    DIRECTIONS_SAMPLE_SPACING = 
    SPATIAL_SLICE_S_VALUE_STEP_SIZE =
    
    def get_spatial_splines(self, sampled_directions_points):
        points_x_values = [point[0] for point in sampled_directions_points]
        points_y_values = [point[1] for point in sampled_directions_points]
        x_array = np.array(points_x_values)
        y_array = np.array(points_y_values)
        initial_end_weights = \
            self.SMOOTHING_SPATIAL_SPLINE_INITIAL_END_WEIGHTS
        initial_smoothing_factor = \
            self.SMOOTHING_SPATIAL_SPLINE_INITIAL_SMOOTHING_FACTOR
        curvature_threshold = config.LATERAL_CURVATURE_CONSTRAINT
        x_spline, y_spline = iterative_smoothing_interpolation_2d(x_array,
                                                                  y_array,
                                                      initial_end_weights,
                                                 initial_smoothing_factor,
                                                      curvature_threshold)
        return [x_spline, y_spline]
    
    def sample_directions_points(self, directions_points):
        sampled_directions_points = interpolate.sample_path(directions_points,
                                               self.DIRECTIONS_SAMPLE_SPACING)
        return sampled_directions_points
   
    def get_spatial_slices_directions_points(self, sampled_directions_points):
        spatial_slices_directions_points = util.smart_sample_nth_points(
            sampled_directions_points, self.SPATIAL_SLICE_S_VALUE_STEP_SIZE)
        return spatial_slices_directions_points
    
    def get_spatial_slices_spline_points(self, sampled_directions_points):        
        spatial_spline_s_values = interpolate.get_s_values(len(
                                        sampled_directions_points))
        spatial_slices_s_values = interpolate.get_slice_s_values(
            spatial_spline_s_values, self.SPATIAL_SLICE_S_VALUE_STEP_SIZE)
        spatial_x_spline, spatial_y_spline = self.get_spatial_splines(
                                               sampled_directions_points)
        spatial_slices_spline_points_x_values = interpolate.get_spline_values(
                          spatial_x_spline, spatial_slices_s_values)
        spatial_slices_spline_points_y_values = interpolate.get_spline_values(
                          spatial_y_spline, spatial_slices_s_values)
        spatial_slices_spline_tuples = zip(
            spatial_slices_spline_points_x_values,
            spatial_slices_spline_points_x_values)
        spatial_slices_spline_points = [list(eachTuple) for eachTuple in
                                            spatial_slices_spline_tuples]
        return spatial_slices_spline_points

    @staticmethod
    def get_spatial_slices_bounds(spatial_slices_directions_points,
                                  spatial_slices_spline_points,
                                  spatial_y_spacing):
        spatial_slices_bounds = []
        for i in range(len(spatial_slices_directions_points)):
            spatial_slice_bounds = {"directions_geospatials":  
                                    spatial_slices_directions_points[i],
                                    "spline_geospatials":
                                    spatial_slices_spline_points[i],
                                    "y_spacing": spatial_y_spacing}
            spatial_slices_bounds.append(spatial_slice_bounds)
        return spatial_slices_bounds        

    def __init__(self, directions_geospatials, spatial_x_spacing,
                                               spatial_y_spacing):
        sampled_directions_geospatials = self.sample_directions_geospatials(
                                                     directions_geospatials)
        spatial_slices_directions_geospatials = \
            SpatialLattice.get_spatial_slices_directions_geospatials(
                                      sampled_directions_geospatials)
        spatial_slices_spline_points = \
            SpatialLattice.get_spatial_slices_spline_points(
                                      sampled_directions_points)         
        spatial_slices_bounds = SpatialLattice.get_spatial_slices_bounds(
                                        spatial_slices_directions_points,
                                        spatial_slices_spline_points,
                                        spatial_y_spacing)
            
