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

class SpatialPath2d(abstract_paths.AbstractPath):
    def __init__(self, spatial_graph, spatial_interpolator):
        abstracti_paths.AbstractPath2d.__init__(self, spatial_graph.geospatials,
                                                   spatial_interpolator)
        self.path_geospatials = self.path_coordinates
        self.path_latlngs = spatial_graph.geospatials_to_latlngs(
                                              self.path_geospatials)
        self.land_cost = landcover.get_land_cost(self.path_latlngs)

class SpatialPathsSet2d(abstract_paths.AbstractPathsSet):
    def __init__(self, spatial_graphs_sets):
        self.start = spatial_graphs_sets.start
        self.end = spatial_graphs_sets.end
        self.start_latlng = spatial_graphs_sets.start_latlng
        self.end_latlng = spatial_graphs_sets.end_latlng
        self.projection = spatial_graphs_sets.projection
        self.spatial_interpolator = spatial_graphs_sets.spatial_interpolator
        abstract_paths.AbstractPathsSet2d.__init(self,
                   spatial_graphs_set.selected_graphs,
                   self.spatial_interpolator,
                   SpatialPath2d)
        
