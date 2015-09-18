"""
Original Developer:
    Jonathan Ward
"""

import abstract_paths
import cacher
import config

class SpatialPath3d(abstract_paths.AbstractPath):

    def __init__(self, tube_coordinates, pylons, path_latlngs, pylon_cost,
                                                    tube_cost, land_cost):
        self.land_cost = land_cost               
        self.path_latlngs = path_latlngs
        self.pylons = pylons
        self.pylon_cost = pylon_cost
        self.tube_coordinates = tube_coordinates
        self.tube_cost = tube_cost

class SpatialPathsSet3d(abstract_paths.AbstractPathsSet):

    def __init__(self, spatial_path_2d, tube_builder):
        self.land_cost = spatial_path_2d.land_cost
        self.path_latlngs = spatial_path_2d.path_latlngs
        self.paths = tube_builder(spatial_path_2d)


class SpatialPathsSets3d(abstract_paths.AbstractPathsSets):
    def __init__(self, spatial_paths_set_2d):
        self.start = spatial_paths_set_2d.start
        self.end = spatial_paths_set_2d.end
        self.start_latlng = spatial_paths_set_2d.start_latlng
        self.end_latlng = spatial_paths_set_2d.end_latlng
        self.tube_builder = spatial_paths_set_2d.tube_builder
        #self.spatial_paths_sets = abstract_paths.AbstractPathsSets.__init__(
        #                                                               self,
                                                             
def get_spatial_paths_sets_3d(spatial_paths_set_2d):
    spatial_paths_set_3d = cacher.get_object("spatial_paths_3d",
                                             SpatialPathsSets3d,
                                             [spatial_paths_set_2d],
                                             config.SPATIAL_PATHS_3D_FLAG)
    return spatial_paths_set_3d
 
