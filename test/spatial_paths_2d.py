"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To create 2d spatial paths (i.e. interpolated spatial graphs)

Last Modified: 
    09/08/15

Last Modified By:
    Jonathan Ward

Last Modification Purpose:
    Created Module
"""

import abstract_paths
import cacher
import config

class SpatialPath2d(abstract_paths.AbstractPath):
    def __init__(self, spatial_graph, spatial_interpolator):
        abstract_paths.AbstractPath.__init__(self, spatial_graph.geospatials,
                                                   spatial_interpolator)        
        self.land_cost = spatial_graph.land_cost
        #self.path_geospatials = self.path_coordinates
        #self.path_latlngs = spatial_graph.geospatials_to_latlngs(
        #                                      self.path_geospatials)
        #self.land_cost = landcover.get_land_cost(self.path_latlngs)

class SpatialPathsSet2d(abstract_paths.AbstractPathsSet):
    def __init__(self, spatial_graphs_sets):
        self.start = spatial_graphs_sets.start
        self.end = spatial_graphs_sets.end
        self.start_latlng = spatial_graphs_sets.start_latlng
        self.end_latlng = spatial_graphs_sets.end_latlng
        self.projection = spatial_graphs_sets.projection
        self.spatial_interpolator = spatial_graphs_sets.interpolator
        abstract_paths.AbstractPathsSet.__init__(self,
                   spatial_graphs_sets,
                   self.spatial_interpolator,
                   SpatialPath2d)
       
def get_spatial_paths_set_2d(spatial_graphs_sets):
    spatial_paths_set_2d = cacher.get_object("spatial_paths_2d",
                                             SpatialPathsSet2d,
                                             [spatial_graphs_sets],
                                             config.SPATIAL_PATHS_2D_FLAG)
    return spatial_paths_set_2d
