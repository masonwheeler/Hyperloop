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

# Custom Modules:
import abstract_paths
import cacher
import config
import elevation
import interpolate
import landcover
import parameters


class SpatialPath2d(abstract_paths.AbstractPath):

    def get_latlngs(self, geospatials_to_latlngs):        
        self.latlngs = geospatials_to_latlngs(self.geospatials)

    def compute_land_cost(self):
        ##needs to handle right of way
        self.land_cost = landcover.get_land_cost(self.latlngs)

    def get_elevation_profile(self, geospatials_to_latlngs):
        undersampled_latlngs = geospatials_to_latlngs(
                            self.undersampled_geospatials)
        self.elevation_profile = elevation.ElevationProfile(
                                           self.geospatials,
                                           undersampled_latlngs,
                                               self.arc_lengths)

    def undersample_graph_geospatials(self, graph_geospatials,
                                         undersampling_factor):
        sample_spacing = parameters.PYLON_SPACING * undersampling_factor
        undersampled_graph_geospatials, undersampled_arc_lengths = \
                    interpolate.sample_path(graph_geospatials, sample_spacing)
        return undersampled_graph_geospatials

    def __init__(self, spatial_graph, spatial_interpolator, base_resolution,
                                                       undersampling_factor):
        graph_geospatials = spatial_graph.elevation_profile.geospatials
        undersampled_graph_geospatials = self.undersample_graph_geospatials(
                                    graph_geospatials, undersampling_factor)
        self.geospatials, self.spatial_curvature_array = \
           spatial_interpolator(undersampled_graph_geospatials, base_resolution)
        #Use underlying graph data:
        self.land_cost = spatial_graph.land_cost
        self.elevation_profile = spatial_graph.elevation_profile

    def to_plottable(self, color_string):
    """Return the physical coordinates of the path in a plottable format
    """
        path_points = zip(*self.geospatials)
        plottable_path = [path_points, color_string]
        return plottable_path


class SpatialPathsSet2d(abstract_paths.AbstractPathsSet):

    NAME = "spatial_paths_2d"
    FLAG = cacher.SPATIAL_PATHS_2D_FLAG
    IS_SKIPPED = cacher.SKIP_PATHS_2D
   
    UNDERSAMPLING_FACTOR = 4
    
    def get_paths_latlngs(self):
        for path in self.paths:
            path.get_latlngs(self.geospatials_to_latlngs)

    def get_paths_elevation_profiles(self):
        for path in self.paths:
            path.get_elevation_profile(self.geospatials_to_latlngs)
 
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
        self.graphs = spatial_graphs_sets.graphs
        self.paths = [SpatialPath2d(graph, self.spatial_interpolator,
             self.spatial_base_resolution, self.UNDERSAMPLING_FACTOR)
        self.get_paths_latlngs()
        self.get_paths_elevation_profiles()        

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
                                             SpatialPathsSet2d.FLAG,
                                             SpatialPathsSet2d.IS_SKIPPED)
    return spatial_paths_set_2d
