"""
Original Developer: Jonathan Ward
Purpose of Module: To generate routes from the lattice edges and merge them.
Last Modified: 8/10/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Changed Class attributes to Instance attributes.
"""

# Standard Modules:
import numpy as np

# Custom Modules: 
import abstract_graphs
import cacher
import curvature_constrain_speed
import elevation
import interpolate
import mergetree
import parameters
import reparametrize_speed
import util


class SpatialGraph(abstract_graphs.AbstractGraph):
    """Stores list of spatial points, their edge costs and curvature"""

    def compute_min_time(self, spatial_curvature_array, tube_curvature_array,
                                                                 arc_lengths):
        max_allowed_speeds_lateral = \
            curvature_constrain_speed.get_lateral_curvature_constrained_speeds(
                                                       spatial_curvature_array)
        max_allowed_speeds_vertical = \
            curvature_constrain_speed.get_vertical_curvature_constrained_speeds(
                                                           tube_curvature_array)
        effective_max_allowed_speeds_by_arc_length = np.minimum(
            max_allowed_speeds_vertical, max_allowed_speeds_lateral)
        time_step_size = 1 #Second
        speeds_by_time, min_time = \
            reparametrize_speed.constrain_and_reparametrize_speeds(
        effective_max_allowed_speeds_by_arc_length, arc_lengths, time_step_size)
        return min_time

    def __init__(self, abstract_graph, land_cost, pylon_cost, tube_cost,
                             tunneling_cost, latlngs, elevation_profile,
                spatial_curvature_array=None, tube_curvature_array=None):
        abstract_graphs.AbstractGraph.__init__(self, abstract_graph.start_id,
                                               abstract_graph.end_id,
                                               abstract_graph.start_angle,
                                               abstract_graph.end_angle,
                                               abstract_graph.abstract_coords,
                                               abstract_graph.physical_coords)
        self.land_cost = land_cost  # The total cost of the land acquired       
        self.pylon_cost = pylon_cost  # The total cost of the pylons
        self.tube_cost = tube_cost
        self.tunneling_cost = tunneling_cost
        self.total_cost = (self.land_cost + self.pylon_cost +
                           self.tube_cost + self.tunneling_cost)
        self.latlngs = latlngs  # The latitude longitude coordinates
        self.elevation_profile = elevation_profile
        arc_lengths = elevation_profile.arc_lengths
        self.tube_curvature_array = tube_curvature_array
        self.spatial_curvature_array = spatial_curvature_array
        if self.spatial_curvature_array == None:
            self.min_time = None
        else:
            self.min_time = self.compute_min_time(spatial_curvature_array, 
                                        tube_curvature_array, arc_lengths)

    def fetch_min_time_and_total_cost(self):
        if self.min_time == None:
            return None
        else:
            min_time = round(self.min_time, 6)
            total_cost = round(self.total_cost / 10.0**6, 6)
            print "min time: " + str(min_time)
            print "total cost: " + str(total_cost)
            return [min_time, total_cost]

    @classmethod
    def init_from_spatial_edge(cls, spatial_edge):
        abstract_edge = spatial_edge.to_abstract_edge()
        abstract_graph = abstract_graphs.AbstractGraph.init_from_abstract_edge(
                                                                 abstract_edge)
        land_cost = spatial_edge.land_cost
        pylon_cost = spatial_edge.pylon_cost
        tube_cost = spatial_edge.tube_cost
        tunneling_cost = spatial_edge.tunneling_cost
        latlngs = spatial_edge.latlngs
        elevation_profile = spatial_edge.elevation_profile        
        tube_curvature_array = spatial_edge.tube_curvature_array
        data = cls(abstract_graph, land_cost, pylon_cost, tube_cost, 
                   tunneling_cost, latlngs, elevation_profile,
                   tube_curvature_array=tube_curvature_array)
        return data

    @staticmethod
    def merge_spatial_curvature_arrays(spatial_graph_a, spatial_graph_b,
                                         graph_interpolator, resolution):
        boundary_geospatials_a = \
            spatial_graph_a.elevation_profile.geospatials_partitions[-1]
        boundary_geospatials_b = \
            spatial_graph_b.elevation_profile.geospatials_partitions[0]
        boundary_a_length = len(boundary_geospatials_a)
        boundary_b_length = len(boundary_geospatials_b)
        merged_boundary_geospatials = util.glue_array_pair(
            boundary_geospatials_a, boundary_geospatials_b)
        interpolated_boundary_geospatials, boundary_spatial_curvature_array = \
            graph_interpolator(merged_boundary_geospatials)
        spatial_curvature_array_a = spatial_graph_a.spatial_curvature_array
        spatial_curvature_array_b = spatial_graph_b.spatial_curvature_array
        boundary_curvatures_a = boundary_spatial_curvature_array[:
                                        boundary_a_length]
        boundary_curvatures_b = boundary_spatial_curvature_array[
                                        -boundary_b_length:]
        if (spatial_curvature_array_a == None and
            spatial_curvature_array_b == None):
            merged_curvature_array = boundary_spatial_curvature_array
        elif (spatial_curvature_array_a != None and
              spatial_curvature_array_b != None):
            spatial_curvature_array_a[-boundary_a_length:] = \
                np.maximum(spatial_curvature_array_a[-boundary_a_length:],
                           boundary_curvatures_a)
            spatial_curvature_array_b[:boundary_b_length] = \
                np.maximum(spatial_curvature_array_b[:boundary_b_length],
                           boundary_curvatures_b)
            merged_curvature_array = util.glue_array_pair(
                                      spatial_curvature_array_a,
                                      spatial_curvature_array_b)
        elif (spatial_curvature_array_a != None and
              spatial_curvature_array_b == None):
            merged_curvature_array = util.glue_array_pair(
                                      spatial_curvature_array_a,
                                      boundary_curvatures_b)
        elif (spatial_curvature_array_a == None and
              spatial_curvature_array_b != None):
            merged_curvature_array = util.glue_array_pair(
                                      boundary_curvatures_a,
                                      spatial_curvature_array_b)
        return merged_curvature_array

    @classmethod
    def merge_two_spatial_graphs(cls, spatial_graph_a, spatial_graph_b,
                                      graph_interpolator, resolution):
        abstract_graph_a = spatial_graph_a.to_abstract_graph()
        abstract_graph_b = spatial_graph_b.to_abstract_graph()
        merged_abstract_graph = \
            abstract_graphs.AbstractGraph.merge_abstract_graphs(
                                 abstract_graph_a, abstract_graph_b)
        land_cost = spatial_graph_a.land_cost + spatial_graph_b.land_cost
        pylon_cost = spatial_graph_a.pylon_cost + spatial_graph_b.pylon_cost
        tube_cost = spatial_graph_a.tube_cost + spatial_graph_b.tube_cost
        tunneling_cost = (spatial_graph_a.tunneling_cost +
                          spatial_graph_b.tunneling_cost)
        latlngs = util.glue_list_pair(spatial_graph_a.latlngs,
                                    spatial_graph_b.latlngs)
        elevation_profile = elevation.ElevationProfile.merge_elevation_profiles(
                                              spatial_graph_a.elevation_profile,
                                              spatial_graph_b.elevation_profile)
        tube_curvature_array = util.glue_array_pair(
                               spatial_graph_a.tube_curvature_array,
                               spatial_graph_b.tube_curvature_array)
        spatial_curvature_array = SpatialGraph.merge_spatial_curvature_arrays(
            spatial_graph_a, spatial_graph_b, graph_interpolator, resolution)
        merged_spatial_graph = cls(merged_abstract_graph, land_cost, pylon_cost,
            tube_cost, tunneling_cost, latlngs,
            elevation_profile, spatial_curvature_array, tube_curvature_array)
        return merged_spatial_graph

    def to_abstract_graph(self):
        abstract_graph = abstract_graphs.AbstractGraph(self.start_id,
                       self.end_id, self.start_angle, self.end_angle,
                          self.abstract_coords, self.physical_coords)
        return abstract_graph


class SpatialGraphsSet(abstract_graphs.AbstractGraphsSet):

    NUM_FRONTS_TO_SELECT = 2
    GRAPH_FILTER_MIN_NUM_EDGES = 2

    def get_spatial_graphs_min_times_and_total_costs(self, spatial_graphs):
        spatial_graphs_min_times_and_total_costs = \
            [spatial_graph.fetch_min_time_and_total_cost()
             for spatial_graph in spatial_graphs]
        if spatial_graphs_min_times_and_total_costs[0] == None:
            return None
        else:
            return spatial_graphs_min_times_and_total_costs
   
    def __init__(self, spatial_graphs, graphs_num_edges):
        abstract_graphs.AbstractGraphsSet.__init__(self, spatial_graphs,
                      self.get_spatial_graphs_min_times_and_total_costs,
                            self.NUM_FRONTS_TO_SELECT, graphs_num_edges,
                                        self.GRAPH_FILTER_MIN_NUM_EDGES)

    @classmethod
    def init_from_spatial_edges_set(cls, spatial_edges_set):
        spatial_graphs = [SpatialGraph.init_from_spatial_edge(spatial_edge)
                                      for spatial_edge in spatial_edges_set]
        graphs_num_edges = 1
        data = cls(spatial_graphs, graphs_num_edges)
        return data


class SpatialGraphsSets(abstract_graphs.AbstractGraphsSets):
   
    NAME = "spatial_graphs"
    FLAG = cacher.SPATIAL_GRAPHS_FLAG
    IS_SKIPPED = cacher.SKIP_GRAPHS
    
    def graph_interpolator(self, graph_geospatials):
        interpolated_geospatials, curvature = self.spatial_interpolator(
                        graph_geospatials, self.spatial_base_resolution)
        return [interpolated_geospatials, curvature]

    def merge_two_spatial_graphs(self, spatial_graph_a, spatial_graph_b):
        merged_spatial_graph = SpatialGraph.merge_two_spatial_graphs(
            spatial_graph_a, spatial_graph_b, self.graph_interpolator,
                                         self.spatial_base_resolution)
        return merged_spatial_graph

    def __init__(self, spatial_edges_sets):
        self.spatial_metadata = spatial_edges_sets.spatial_metadata
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
