"""
Original Developer:
    Jonathan Ward
"""

import cacher
import config
import util


class SpatialPath3d(object):

    def __init__(self, tube_profile, spatial_path_2d):
        self.land_cost = spatial_path_2d.land_cost
        self.latlngs = spatial_path_2d.latlngs
        self.geospatials = spatial_path_2d.geospatials
        self.pylons = tube_profile.pylons
        self.pylon_cost = tube_profile.pylon_cost
        self.tube_coords = tube_profile.tube_coords
        self.tube_cost = tube_profile.tube_cost
        self.land_elevations = tube_profile.land_elevations
        self.arc_lengths = tube_profile.arc_lengths

class SpatialPathsSet3d(object):
  
    def build_tube_profiles_v1(self, tube_builder, elevation_profile):
        tube_profile = tube_builder(elevation_profile)
        tube_profiles = [tube_profile]
        return tube_profiles

    def build_paths(self, spatial_path_2d, tube_profiles):
        self.paths = [SpatialPath3d(tube_profile, spatial_path_2d)
                      for tube_profile in tube_profiles]

    def __init__(self, spatial_path_2d, tube_builder):
        elevation_profile = spatial_path_2d.elevation_profile 
        tube_profiles = self.build_tube_profiles_v1(tube_builder,
                                                    elevation_profile)
        self.build_paths(spatial_path_2d, tube_profiles)


class SpatialPathsSets3d(object):

    NAME = "spatial_paths_3d"
    FLAG = cacher.SPATIAL_PATHS_3D_FLAG

    def build_paths_sets(self, spatial_paths_2d, tube_builder):
        ##print("Num paths: " + str(len(spatial_paths_2d)))
        self.paths_sets = [SpatialPathsSet3d(spatial_path_2d, tube_builder)
                           for spatial_path_2d in spatial_paths_2d]      
        
    def select_paths(self):
        paths_lists = [paths_set.paths for paths_set in self.paths_sets]
        paths = util.fast_concat(paths_lists)
        self.selected_paths = paths

    def __init__(self, spatial_paths_set_2d):
        self.start = spatial_paths_set_2d.start
        self.end = spatial_paths_set_2d.end
        self.start_latlng = spatial_paths_set_2d.start_latlng
        self.end_latlng = spatial_paths_set_2d.end_latlng
        tube_builder = spatial_paths_set_2d.tube_builder
        self.undersampling_factor = spatial_paths_set_2d.UNDERSAMPLING_FACTOR
        self.build_paths_sets(spatial_paths_set_2d.paths, tube_builder)
        self.select_paths()
        
                                                             
def get_spatial_paths_sets_3d(*args):
    spatial_paths_set_3d = cacher.get_object(SpatialPathsSets3d.NAME,
                                             SpatialPathsSets3d,
                                             args,
                                             SpatialPathsSets3d.FLAG)
    return spatial_paths_set_3d
 
