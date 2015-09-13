"""
Original Developer:
    Jonathan Ward
"""

import abstract_paths

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
        self.tube_options = tube_builder(spatial_path_2d)


class SpatialPathsSets3d(abstract_paths.AbstractPathsSets):
    def __init__(self, spatial_paths_set_2d):
        pass                
        
