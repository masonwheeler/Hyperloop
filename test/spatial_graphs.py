"""
Original Developer: Jonathan Ward
Purpose of Module: To generate routes from the lattice edges and merge them.
Last Modified: 8/10/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Changed Class attributes to Instance attributes.
"""

# Custom Modules: 

import abstract_graphs
import cacher
import curvature
import elevation
import mergetree
import util
import velocity


class SpatialGraph(abstract_graphs.AbstractGraph):
    """Stores list of spatial points, their edge costs and curvature"""
    
    GRAPH_SAMPLE_SPACING = 1000 #Meters

    def compute_min_time_and_total_cost(self, spatial_curvature_array,
                                             tube_curvature_array):
        max_allowed_vels = \
            curvature.lateral_curvature_array_to_max_allowed_vels(
                                              spatial_curvature_array)
        time_checkpoints = \
            velocity.velocities_by_arc_length_to_time_checkpoints(
                                        max_allowed_vels, arc_lengths)
        self.min_time = time_checkpoints[-1]
        self.total_cost = self.pylon_cost + self.tube_cost + self.land_cost

    def __init__(self, abstract_graph, pylon_cost, tube_cost, land_cost,
                       latlngs, geospatials, elevation_profile,
                       spatial_curvature_array=None, tube_curvature_array=None):
        abstract_graphs.AbstractGraph.__init__(self, abstract_graph.start_id,
                                               abstract_graph.end_id,
                                               abstract_graph.start_angle,
                                               abstract_graph.end_angle,
                                               abstract_graph.num_edges,
                                               abstract_graph.abstract_coords)
        self.pylon_cost = pylon_cost  # The total cost of the pylons
        self.tube_cost = tube_cost
        self.land_cost = land_cost  # The total cost of the land acquired       
        self.latlngs = latlngs  # The latitude longitude coordinates
        self.geospatials = geospatials  # The geospatial coordinates
        self.elevation_profile = elevation_profile
        self.tube_curvature_array = tube_curvature_array
        if spatial_curvature_array == None:
            self.min_time = None
        else:
            self.spatial_curvature_array = spatial_curvature_array
            self.compute_min_time_and_total_cost(self.spatial_curvature_array,
                                             self.tube_curvature_array)

    def fetch_min_time_and_total_cost(self):
        return [self.min_time, self.total_cost]

    @classmethod
    def init_from_spatial_edge(cls, spatial_edge):
        abstract_edge = spatial_edge.to_abstract_edge()
        abstract_graph = abstract.AbstractGraph.init_from_abstract_edge(
                                                          abstract_edge)
        pylon_cost = spatial_edge.pylon_cost
        tube_cost = spatial_edge.tube_cost       
        land_cost = spatial_edge.land_cost
        latlngs = spatial_edge.latlngs
        geospatials_partitions = [spatial_edge.geospatials]
        elevation_profile = spatial_edge.elevation_profile
        tube_curvature_array = spatial_edge.tube_curvature_array
        data = cls(abstract_graph, pylon_cost, tube_cost, land_cost,
            latlngs, geospatials_partitions, arc_lengths, elevation_profile,
                                  tube_curvature_array=tube_curvature_array)
        return data

    @staticmethod
    def merge_spatial_curvature_arrays(spatial_graph_a, spatial_graph_b,
                                         graph_interpolator, resolution):
        boundary_edge_geospatials_a = \
            spatial_graph_a.geospatials_partitions[-1]
        boundary_edge_geospatials_b = \
            spatial_graph_b.geospatials_partitions[0]
        sampled_boundary_edge_geospatials_a, boundary_arc_lengths_a = \
            interpolate.sample_path(boundary_edge_geospatials_a, resolution)
        sampled_boundary_edge_geospatials_b, boundary_arc_lengths_b = \
            interpolate.sample_path(boundary_edge_geospatials_b, resolution)
        boundary_a_length = len(boundary_arc_lengths_a)
        sampled_boundary_geospatials = util.smart_concat(
                                        sampled_boundary_edge_geospatials_a
                                        sampled_boundary_edge_geospatials_b)
        (interpolated_boundary_geospatials, 
        spatial_boundary_curvature_array,
        boundary_arc_lengths) = graph_interpolator(sampled_boundary_geospatials)
        spatial_curvature_array_a = spatial_graph_a.spatial_curvature_array_a
        spatial_curvature_array_b = spatial_graph_b.spatial_curvature_array_b
        boundary_curvatures_a = spatial_boundary_curvature_array[:
                                        boundary_a_length]
        boundary_curvatures_b = spatial_boundary_curvature_array[
                                        boundary_a_length:]
        if (spatial_curvature_array_a == None and
            spatial_curvature_array_b == None):
            merged_curvature_array = spatial_boundary_curvature_array
        if (spatial_curvature_array_a != None and
            spatial_curvature_array_b != None):
            spatial_curvature_array_a[-boundary_a_length:] =
            (spatial_curvature_array_a[-boundary_a_length:] +
             boundary_curvatures_a) / 2.0
            spatial_curvature_array_b[:boundary_a_length] =
            (spatial_curvature_array_b[:boundary_a_length] +
             boundary_curvatures_b) / 2.0
            merged_curvature_array = (spatial_curvature_array_a +
                                      spatial_curvature_array_b)
        if (spatial_curvature_array_a != None and
            spatial_curvature_array_b == None):             
            merged_curvature_array = (spatial_curvature_array_a +
                                      boundary_curvatures_b)
        if (spatial_curvature_array_a == None and
            spatial_curvature_array_b != None):             
            merged_curvature_array = (boundary_curvatures_a +
                                      spatial_curvature_array_b)
        return merged_curvature_array

    @classmethod
    def merge_two_spatial_graphs(cls, spatial_graph_a, spatial_graph_b,
                                      graph_interpolator, resolution):
        abstract_graph_a = spatial_graph_a.to_abstract_graph()
        abstract_graph_b = spatial_graph_b.to_abstract_graph()
        merged_abstract_graph = abstract.AbstractGraph.merge_abstract_graphs(
                                          abstract_graph_a, abstract_graph_b)
        pylon_cost = spatial_graph_a.pylon_cost + spatial_graph_b.pylon_cost
        tube_cost = spatial_graph_a.tube_cost + spatial_graph_b.tube_cost
        land_cost = spatial_graph_a.land_cost + spatial_graph_b.land_cost
        latlngs = util.smart_concat(spatial_graph_a.latlngs,
                                    spatial_graph_b.latlngs)
        geospatials_partitions = (spatial_graph_a.geospatials_partitions +
                                  spatial_graph_b.geospatials_partitions)
        elevation_profile = elevation.ElevationProfile.merge_elevation_profiles(
                                              spatial_graph_a.elevation_profile,
                                              spatial_graph_b.elevation_profile)
        tube_curvature_array = util.smart_concat(
                               spatial_graph_a.tube_curvature_array,
                               spatial_graph_b.tube_curvature_array)
        spatial_curvature_array = SpatialGraph.merge_spatial_curvature_arrays(
            spatial_graph_a, spatial_graph_b, graph_interpolator, resolution)
        merged_spatial_graph = cls(merged_abstract_graph, pylon_cost,
           tube_cost, land_cost, latlngs, geospatials_partitions,
           elevation_profile, spatial_curvature_array, tube_curvature_array)
        return merged_spatial_graph

    def to_abstract_graph(self):
        abstract_graph = abstract.AbstractGraph(self.start_id,
                                                self.end_id,
                                                self.start_angle,
                                                self.end_angle,
                                                self.num_edges,
                                                self.abstract_coords)
        return abstract_graph

    def to_plottable(self, color_string):
        """Return the geospatial coords of the graph in plottable format"""
        geospatials_x_vals = [geospatial[0] for geospatial in self.geospatials]
        geospatials_y_vals = [geospatial[1] for geospatial in self.geospatials]
        graph_points = [geospatials_x_vals, geospatials_y_vals]
        plottable_graph = [graph_points, color_string]
        return plottable_graph


class SpatialGraphsSet(abstract_graphs.AbstractGraphsSet):
    NUM_FRONTS_TO_SELECT = 5

    def get_spatial_graphs_min_times_and_total_costs(self, spatial_graphs):
        spatial_graphs_min_times_and_total_costs = \
            [spatial_graph.fetch_min_time_and_total_cost()
             for spatial_graph in spatial_graphs]
        return spatial_graphs_min_times_and_total_costs

    def __init__(self, spatial_graphs, spatial_graphs_num_edges,
                                       spatial_interpolator):
        minimize_cost = True
        minimize_time = True        
        abstract_graphs.AbstractGraphsSet.__init__(self, spatial_graphs,
                                                   spatial_graphs_num_edges,
                                            self.get_spatial_graphs_cost_time,
                                                   spatial_interpolator,
                                                   minimize_cost,
                                                   minimize_time,
                                                   self.NUM_FRONTS_TO_SELECT)

    @classmethod
    def init_from_spatial_edges_set(cls, spatial_edges_set,
                                         spatial_interpolator):
        spatial_graphs = [SpatialGraph.init_from_spatial_edge(spatial_edge)
                                      for spatial_edge in spatial_edges_set]
        spatial_graphs_num_edges = 1
        data = cls(spatial_graphs, spatial_graphs_num_edges,
                                   spatial_interpolator)
        return data


class SpatialGraphsSets(abstract_graphs.AbstractGraphsSets):
   
    NAME = "spatial_graphs"
    FLAG = cacher.SPATIAL_GRAPHS_FLAG
    IS_SKIPPED = cacher.SKIP_GRAPHS
    
    def graph_interpolator(self, graph_geospatials):
        interpolated_geospatials, curvature, arc_lengths = \
            self.spatial_interpolator(graph_geospatials,
                                      self.spatial_base_resolution)
        return [interpolated_geospatials, curvature, arc_lengths]

    def merge_two_spatial_graphs(self, spatial_graph_a, spatial_graph_b):
        merged_spatial_graph = SpatialGraph.merge_two_spatial_graphs(
            spatial_graph_a, spatial_graph_b, self.graph_interpolator,
                                         self.spatial_base_resolution)
        return merged_spatial_graph

    def __init__(self, spatial_edges_sets):
        self.start = spatial_edges_sets.start
        self.end = spatial_edges_sets.end
        self.start_latlng = spatial_edges_sets.start_latlng
        self.end_latlng = spatial_edges_sets.end_latlng
        self.geospatials_to_latlngs = spatial_edges_sets.geospatials_to_latlngs
        self.spatial_interpolator = spatial_edges_sets.spatial_interpolator
        self.tube_builder = spatial_edges_sets.tube_builder
        self.spatial_base_resolution = \
            spatial_edges_sets.spatial_base_resolution
        abstract_graphs.AbstractGraphsSets.__init__(self, spatial_edges_sets,
                            SpatialGraphsSet.init_from_spatial_edges_set,
                            self.merge_two_spatial_graphs,
                            SpatialGraphsSet)

    def get_plottable_graphs(self, color_string):
        plottable_graphs = []
        for graph in self.selected_graphs:
            plottable_graph = graph.to_plottable(color_string)
            plottable_graphs.append(plottable_graph)
        return plottable_graphs

    def get_cost_time_scatterplot(self, color_string):
        costs = []
        times = []
        for graph in self.selected_graphs:
            costs.append(graph.total_cost)
            times.append(graph.time)
        scatterplot_values = [costs, times]
        scatterplot = [scatterplot_values, color_string]
        return scatterplot
        

def get_spatial_graphs_sets(*args):
    spatial_graphs_sets = cacher.get_object(SpatialGraphsSets.NAME,
                                            SpatialGraphsSets,
                                            args,
                                            SpatialGraphsSets.FLAG,
                                            SpatialGraphsSets.IS_SKIPPED)
    return spatial_graphs_sets
