"""
Original Developer:
    Jonathan Ward
"""

# Standard Modules:
import numpy as np

# Custom Modules:
import cacher
import config
import curvature_constrain_speed
import parameters
import paretofront
import util
import reparametrize_speed


class SpatialPath3d(object):

    def compute_min_time(self, spatial_curvature_array, tube_curvature_array,
                                                                 arc_lengths):
        max_allowed_speeds_lateral = \
            curvature_constrain_speed.get_lateral_curvature_constrained_speeds(
                                                       spatial_curvature_array)
        max_allowed_speeds_vertical = \
            curvature_constrain_speed.get_vertical_curvature_constrained_speeds(
                                                           tube_curvature_array)
        max_allowed_speeds = np.minimum(max_allowed_speeds_vertical, 
                                        max_allowed_speeds_lateral)
        time_step_size = 1 #Second
        speeds_by_time, min_time = \
            reparametrize_speed.constrain_and_reparametrize_speeds(
                   max_allowed_speeds, arc_lengths, time_step_size)
        return [min_time, max_allowed_speeds]

    def compute_total_cost(self):
        total_cost = (self.land_cost + self.pylon_cost +
                      self.tube_cost + self.tunneling_cost)
        return total_cost

    def get_tube_coords(self, tube_elevations, geospatials):
        x_coords, y_coords = np.transpose(geospatials)
        z_coords = tube_elevations
        tube_coords = np.transpose([x_coords, y_coords, z_coords])
        return tube_coords

    def __init__(self, tube_profile, spatial_path_2d):
        geospatials = spatial_path_2d.geospatials
        tube_elevations = tube_profile.tube_elevations
        self.land_cost = spatial_path_2d.land_cost
        self.pylon_cost = tube_profile.total_pylon_cost
        self.tube_cost = tube_profile.tube_cost
        self.tunneling_cost = tube_profile.tunneling_cost
        self.latlngs = spatial_path_2d.latlngs
        self.pylons = tube_profile.build_pylons()
        self.land_elevations = tube_profile.land_elevations
        self.arc_lengths = tube_profile.arc_lengths
        self.spatial_curvature_array = spatial_path_2d.spatial_curvature_array
        self.tube_curvature_array = tube_profile.tube_curvature_array
        self.min_time, self.max_allowed_speeds = self.compute_min_time(
            self.spatial_curvature_array, self.tube_curvature_array, 
                                                   self.arc_lengths)
        self.total_cost = self.compute_total_cost()
        self.tube_coords = self.get_tube_coords(tube_elevations, geospatials)
        self.tube_elevations = tube_elevations

    def fetch_min_time_and_total_cost(self):
        min_time = round(self.min_time / 60.0, 3)
        total_cost = round(self.total_cost / 10.0**9, 3)
        return [min_time, total_cost]

import time

class SpatialPathsSet3d(object):
  
    NUM_TUBE_PROFILES = 5
    """
    DEFAULT_MAX_CURVATURE = (parameters.MAX_VERTICAL_ACCEL /
                             parameters.MAX_SPEED**2)
    """

    def build_tube_profiles(self, tube_builder, elevation_profile):
        tube_profile = tube_builder(elevation_profile)
        tube_profiles = [tube_profile]
        return tube_profiles

    def build_paths(self, spatial_path_2d, tube_profiles):
        paths = [SpatialPath3d(tube_profile, spatial_path_2d)
                 for tube_profile in tube_profiles]
        return paths

    def __init__(self, spatial_path_2d, tube_builder):
        elevation_profile = spatial_path_2d.elevation_profile 
        tube_profiles = self.build_tube_profiles(tube_builder, 
                                            elevation_profile)
        self.paths = self.build_paths(spatial_path_2d, tube_profiles)


class SpatialPathsSets3d(object):

    NAME = "spatial_paths_3d"
    FLAG = cacher.SPATIAL_PATHS_3D_FLAG
    IS_SKIPPED = cacher.SKIP_PATHS_3D

    def build_paths_sets(self, spatial_paths_2d, tube_builder):
        print("Num paths 2d: " + str(len(spatial_paths_2d)))
        paths_sets = [SpatialPathsSet3d(spatial_path_2d, tube_builder)
                           for spatial_path_2d in spatial_paths_2d]
        return paths_sets
        
    def select_paths(self, paths_sets):
        paths_lists = [paths_set.paths for paths_set in paths_sets]
        paths = util.fast_concat(paths_lists)
        print "num paths 3d: " + str(len(paths))
        paths_times_and_costs = [path.fetch_min_time_and_total_cost()
                                 for path in paths]
        front = paretofront.ParetoFront(paths_times_and_costs)
        optimal_paths_indices = front.fronts_indices[-1]
        optimal_paths = [paths[i] for i in optimal_paths_indices]
        sorted_paths = sorted(optimal_paths, key=lambda p: p.total_cost)
        print "num paths 3d selected: " + str(len(sorted_paths))
        return sorted_paths

    def __init__(self, spatial_paths_set_2d):
        self.spatial_metadata = spatial_paths_set_2d.spatial_metadata
        paths_sets = self.build_paths_sets(spatial_paths_set_2d.paths[0:2],
                                           spatial_paths_set_2d.tube_builder)
        self.selected_paths = self.select_paths(paths_sets)
        
                                                             
def get_spatial_paths_sets_3d(*args):
    spatial_paths_set_3d = cacher.get_object(SpatialPathsSets3d.NAME,
                                             SpatialPathsSets3d,
                                             args,
                                             SpatialPathsSets3d.FLAG,
                                             SpatialPathsSets3d.IS_SKIPPED)
    return spatial_paths_set_3d
 
