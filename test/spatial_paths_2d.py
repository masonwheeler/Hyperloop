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

# Standard Modules:
import numpy as np

# Custom Modules:
import cacher
import config
##import elevation
##import landcover
import parameters
import util


class SpatialPath2d(object):

    def compute_total_distance(self, geospatials):
        geospatial_edges = util.to_pairs(geospatials)
        geospatial_vectors = [edge[1] - edge[0] for edge in geospatial_edges]
        edge_lengths = np.linalg.norm(geospatial_vectors, axis=1)
        total_distance = np.sum(edge_lengths)
        return total_distance

    def __init__(self, spatial_graph, spatial_interpolator, base_resolution,
                                                     geospatials_to_latlngs):
        graph_geospatials = spatial_graph.elevation_profile.geospatials
        self.arc_lengths = spatial_graph.elevation_profile.arc_lengths
        geospatials, spatial_curvature_array = spatial_interpolator(
                          graph_geospatials, parameters.MAX_LATERAL_CURVATURE)
        self.total_distance = self.compute_total_distance(geospatials)
        self.spatial_curvature_array = spatial_curvature_array
        self.geospatials = geospatials
        self.latlngs = geospatials_to_latlngs(geospatials)
        self.land_cost = spatial_graph.land_cost
        self.elevation_profile = spatial_graph.elevation_profile
        #self.elevation_profile = elevation.ElevationProfile(
        #  self.geospatials, self.latlngs, self.arc_lengths)

    def to_plottable(self, color_string):
        """Return the physical coordinates of the path in a plottable format
        """
        path_points = zip(*self.geospatials)
        plottable_path = [path_points, color_string]
        return plottable_path


class SpatialPathsSet2d(object):

    NAME = "spatial_paths_2d"
    FLAG = cacher.SPATIAL_PATHS_2D_FLAG
    IS_SKIPPED = cacher.SKIP_PATHS_2D

    def __init__(self, spatial_graphs_sets):
        self.spatial_metadata = spatial_graphs_sets.spatial_metadata
        self.geospatials_to_latlngs = spatial_graphs_sets.geospatials_to_latlngs
        self.spatial_interpolator = spatial_graphs_sets.spatial_interpolator
        self.tube_builder = spatial_graphs_sets.tube_builder
        self.spatial_base_resolution = \
            spatial_graphs_sets.spatial_base_resolution
        self.graphs = spatial_graphs_sets.selected_graphs
        print "num graphs: " + str(len(self.graphs))
        self.paths = [SpatialPath2d(graph, self.spatial_interpolator,
             self.spatial_base_resolution, self.geospatials_to_latlngs)
                      for graph in self.graphs]

    def get_plottable_graphs(self, color_string):
        plottable_graphs = []
        for graph in self.graphs:
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
