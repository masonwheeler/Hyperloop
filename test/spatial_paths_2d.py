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
    def __init__(self, spatial_graph, spatial_interpolator, base_resolution):
        abstract_paths.AbstractPath.__init__(self, spatial_graph.geospatials,
                                       spatial_interpolator, base_resolution)
        self.land_cost = spatial_graph.land_cost
        self.geospatials = self.path_coordinates  
        self.path_latlngs = spatial_graph.geospatials_to_latlngs(
                                              self.path_geospatials)
        #land_cost_v2 = landcover.get_land_cost(self.path_latlngs)

class SpatialPathsSet2d(abstract_paths.AbstractPathsSet):
    def __init__(self, spatial_graphs_sets):
        self.start = spatial_graphs_sets.start
        self.end = spatial_graphs_sets.end
        self.start_latlng = spatial_graphs_sets.start_latlng
        self.end_latlng = spatial_graphs_sets.end_latlng
        self.projection = spatial_graphs_sets.projection
        self.spatial_interpolator = spatial_graphs_sets.spatial_interpolator
        self.tube_builder = spatial_graphs_sets.tube_builder
        self.spatial_base_resolution = \
            spatial_graphs_sets.spatial_base_resolution
        abstract_paths.AbstractPathsSet.__init__(self,
                   spatial_graphs_sets,
                   self.spatial_interpolator,
                   self.spatial_base_resolution,
                   SpatialPath2d)

    def get_plottable_graphs(self, color_string):
        plottable_graphs = []
        for graph in self.underlying_graphs:
            plottable_graph = graph.to_plottable(color_string)
            plottable_graphs.append(plottable_graph)
        return plottable_graphs

    def get_plottable_paths(self, color_string):
        plottable_paths = []
        for path in self.paths:
            plottable_path = path.to_plottable(color_string)
            plottable_paths.append(plottable_path)
        return plottable_paths
       
def get_spatial_paths_set_2d(spatial_graphs_sets):
    spatial_paths_set_2d = cacher.get_object("spatial_paths_2d",
                                             SpatialPathsSet2d,
                                             [spatial_graphs_sets],
                                             config.SPATIAL_PATHS_2D_FLAG)
    return spatial_paths_set_2d
