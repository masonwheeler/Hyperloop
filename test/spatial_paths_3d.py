"""
Original Developer:
    Jonathan Ward
"""

import abstract_paths
import cacher
import config
import util

import time

class SpatialPath3d(abstract_paths.AbstractPath):

    def __init__(self, tube_profile, latlngs, geospatials, land_cost):
        self.land_cost = land_cost 
        self.latlngs = latlngs
        self.geospatials = geospatials
        self.pylons = tube_profile.pylons
        self.total_pylon_cost = tube_profile.pylon_cost
        self.tube_coords = tube_profile.tube_coords
        self.tube_cost = tube_profile.tube_cost
        self.land_elevations = tube_profile.land_elevations

class SpatialPathsSet3d(abstract_paths.AbstractPathsSet):
  
    def build_tube_profiles_v1(self):
        start = time.time()
        tube_profile = self.tube_builder(self.elevation_profile)
        self.tube_profiles = [tube_profile]

    def build_paths(self):
        self.paths = [SpatialPath3d(tube_profile, self.latlngs,
                                    self.geospatials, self.land_cost)
                      for tube_profile in self.tube_profiles]

    def __init__(self, spatial_path_2d, tube_builder):
        self.tube_builder = tube_builder
        self.land_cost = spatial_path_2d.land_cost
        self.latlngs = spatial_path_2d.latlngs
        self.geospatials = spatial_path_2d.geospatials
        self.elevation_profile = spatial_path_2d.elevation_profile        
        self.build_tube_profiles_v1()
        self.build_paths()


class SpatialPathsSets3d(object):

    NAME = "spatial_paths_3d"
    FLAG = cacher.SPATIAL_PATHS_3D_FLAG

    def build_paths_sets(self, spatial_paths_2d):
        print("Num paths: " + str(len(spatial_paths_2d)))
        self.paths_sets = [SpatialPathsSet3d(spatial_path_2d, self.tube_builder)
                           for  spatial_path_2d in spatial_paths_2d]      
        
    def select_paths(self):
        paths_lists = [paths_set.paths for paths_set in self.paths_sets]
        paths = util.fast_concat(paths_lists)
        self.selected_paths = paths

    def __init__(self, spatial_paths_set_2d):
        self.start = spatial_paths_set_2d.start
        self.end = spatial_paths_set_2d.end
        self.start_latlng = spatial_paths_set_2d.start_latlng
        self.end_latlng = spatial_paths_set_2d.end_latlng
        self.tube_builder = spatial_paths_set_2d.tube_builder
        self.undersampling_factor = spatial_paths_set_2d.UNDERSAMPLING_FACTOR
        self.build_paths_sets(spatial_paths_set_2d.paths)
        self.select_paths()
        
                                                             
def get_spatial_paths_sets_3d(*args):
    spatial_paths_set_3d = cacher.get_object(SpatialPathsSets3d.NAME,
                                             SpatialPathsSets3d,
                                             args,
                                             SpatialPathsSets3d.FLAG)
    return spatial_paths_set_3d
 
