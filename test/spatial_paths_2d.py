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

    def get_latlngs(self, geospatials_to_latlngs):        
        self.latlngs = geospatials_to_latlngs(self.geospatials)

    def compute_land_cost(self):              
        self.land_cost = landcover.get_land_cost(self.path_latlngs)

    def get_elevation_profile(self, geospatials_to_latlngs):
        sampled_geospatials = interpolate.sample_points(self.geospatials)
        sampled_latlngs = geospatials_to_latlngs
        #elevation_profile = elevation.get_elevation_profile(sampled_geospatials,                        
    def __init__(self, spatial_graph, spatial_interpolator, base_resolution):
        abstract_paths.AbstractPath.__init__(self, spatial_graph.geospatials,
                                       spatial_interpolator, base_resolution)
        self.geospatials = self.path_coordinates 
        self.land_cost = spatial_graph.land_cost
        self.elevation_profile = spatial_graph.elevation_profile 


class SpatialPathsSet2d(abstract_paths.AbstractPathsSet):

    NAME = "spatial_paths_2d"
    FLAG = cacher.SPATIAL_PATHS_2D_FLAG
   
    def get_paths_latlngs(self):
        for path in self.paths:
            path.get_latlngs(self.geospatials_to_latlngs)
 
    def __init__(self, spatial_graphs_sets):
        self.start = spatial_graphs_sets.start
        self.end = spatial_graphs_sets.end
        self.start_latlng = spatial_graphs_sets.start_latlng
        self.end_latlng = spatial_graphs_sets.end_latlng
        self.geospatials_to_latlngs = spatial_graphs_sets.geospatials_to_latlngs
        self.spatial_interpolator = spatial_graphs_sets.spatial_interpolator
        self.tube_builder = spatial_graphs_sets.tube_builder
        self.spatial_base_resolution = \
            spatial_graphs_sets.spatial_base_resolution
        abstract_paths.AbstractPathsSet.__init__(self,
                                  spatial_graphs_sets,
                            self.spatial_interpolator,
                         self.spatial_base_resolution,
                                        SpatialPath2d)
        self.get_paths_latlngs()

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
       
def get_spatial_paths_set_2d(*args):
    spatial_paths_set_2d = cacher.get_object(SpatialPathsSet2d.NAME,
                                             SpatialPathsSet2d,
                                             args,
                                             SpatialPathsSet2d.FLAG)
    return spatial_paths_set_2d
