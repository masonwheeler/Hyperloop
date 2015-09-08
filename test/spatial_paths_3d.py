"""
Original Developer:
    Jonathan Ward
"""

import abstract
import tube

class SpatialPath3d(abstract.AbstractPath):
    def __init__(self, spatial_path_2d, tube_builder):
        self.path_latlngs = spatial_path_2d.path_latlngs
        self.path_geospatials = spatial_path_2d.path_geospatials
        self.land_cost = spatial_path_2d.land_cost
        tube
