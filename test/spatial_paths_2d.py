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

import abstract
import spatial_interpolate

class SpatialPath2d(abstract.AbstractPath):
    def __init__(self, spatial_graph, spatial_interpolator):
        abstract.AbstractPath2d.__init__(self, spatial_graph.geospatials,
                                                   spatial_interpolator)
        self.path_geospatials = self.path_coordinates
        self.path_latlngs = spatial_graph.geospatials_to_latlngs(
                                              self.path_geospatials)
        self.land_cost = landcover.get_land_cost(self.path_latlngs)

class SpatialPathsSet2d(abstract.AbstractPathsSet):
    def __init__(self, spatial_graphs_set, spatial_interpolator):        
        abstract.AbstractPathsSet2d.__init(self, spatial_graphs_set.graphs,
                                spatial_interpolator, SpatialPath2d)

