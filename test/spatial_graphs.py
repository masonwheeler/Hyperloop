"""
Original Developer: Jonathan Ward
Purpose of Module: To generate routes from the lattice edges and merge them.
Last Modified: 8/10/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Changed Class attributes to Instance attributes.
"""

import abstract_graphs as abstract
import cacher
import config
import elevation
import interpolate
import mergetree
import paretofront
import util
import visualize

class SpatialGraph(abstract.AbstractGraph):
    """Stores list of spatial points, their edge costs and curvature"""
    
    GRAPH_SAMPLE_SPACING = 1000 #Meters

    def __init__(self, abstract_graph, pylon_cost, tube_cost, land_cost,
                               latlngs, geospatials, elevation_profile):
        abstract.AbstractGraph.__init__(self, abstract_graph.start_id,
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

    @classmethod
    def init_from_spatial_edge(cls, spatial_edge):
        abstract_edge = spatial_edge.to_abstract_edge()
        abstract_graph = abstract.AbstractGraph.init_from_abstract_edge(
                                                          abstract_edge)
        pylon_cost = spatial_edge.pylon_cost
        tube_cost = spatial_edge.tube_cost
        land_cost = spatial_edge.land_cost
        latlngs = spatial_edge.latlngs
        geospatials = spatial_edge.geospatials
        elevation_profile = spatial_edge.elevation_profile
        data = cls(abstract_graph, pylon_cost, tube_cost, land_cost,
                            latlngs, geospatials, elevation_profile)
        return data

    def to_abstract_graph(self):
        abstract_graph = abstract.AbstractGraph(self.start_id,
                                                self.end_id,
                                                self.start_angle,
                                                self.end_angle,
                                                self.num_edges,
                                                self.abstract_coords)
        return abstract_graph

    def get_cost_and_time(self, spatial_interpolator):
        #interpolated_geospatials = interpolate_spatial_graph(geospatials)
        #spatial_curvature = compute_spatial_curvature(interpolated_geospatials)
        #max_velocities
        #time = triptime.compute_spatial_graph_time(geospatials)
        self.time = interpolate.graph_curvature(self.geospatials,
                                           self.GRAPH_SAMPLE_SPACING)
        self.total_cost = self.pylon_cost + self.tube_cost + self.land_cost
        return [self.total_cost, self.time]

    def to_plottable(self, color_string):
        """Return the geospatial coords of the graph in plottable format"""
        geospatials_x_vals = [geospatial[0] for geospatial in self.geospatials]
        geospatials_y_vals = [geospatial[1] for geospatial in self.geospatials]
        graph_points = [geospatials_x_vals, geospatials_y_vals]
        plottable_graph = [graph_points, color_string]
        return plottable_graph


class SpatialGraphsSet(abstract.AbstractGraphsSet):
    NUM_FRONTS_TO_SELECT = 5
    SPATIAL_GRAPH_FILTER_MIN_NUM_EDGES = 3

    def get_spatial_graphs_cost_time(self, spatial_graphs,
                                           spatial_graphs_num_edges,
                                           spatial_interpolator):
        if spatial_graphs_num_edges < self.SPATIAL_GRAPH_FILTER_MIN_NUM_EDGES:
            return None
        else:
            spatial_graphs_costs_and_times = [spatial_graph.get_cost_and_time(
                                              spatial_interpolator)
                                            for spatial_graph in spatial_graphs]
            return spatial_graphs_costs_and_times

    def __init__(self, spatial_graphs, spatial_graphs_num_edges,
                                       spatial_interpolator):
        minimize_cost = True
        minimize_time = True        
        abstract.AbstractGraphsSet.__init__(self, spatial_graphs,
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


class SpatialGraphsSets(abstract.AbstractGraphsSets):
   
    NAME = "spatial_graphs"
    FLAG = cacher.SPATIAL_GRAPHS_FLAG
    IS_SKIPPED = cacher.SKIP_GRAPHS
 
    @staticmethod
    def merge_two_spatial_graphs(spatial_graph_a, spatial_graph_b):
        abstract_graph_a = spatial_graph_a.to_abstract_graph()
        abstract_graph_b = spatial_graph_b.to_abstract_graph()
        merged_abstract_graph = abstract.AbstractGraph.merge_abstract_graphs(
                                          abstract_graph_a, abstract_graph_b)
        pylon_cost = spatial_graph_a.pylon_cost + spatial_graph_b.pylon_cost
        tube_cost = spatial_graph_a.tube_cost + spatial_graph_b.tube_cost
        land_cost = spatial_graph_a.land_cost + spatial_graph_b.land_cost
        latlngs = util.smart_concat(spatial_graph_a.latlngs,
                                    spatial_graph_b.latlngs)
        geospatials = util.smart_concat(spatial_graph_a.geospatials,
                                        spatial_graph_b.geospatials)
        elevation_profile = elevation.ElevationProfile.merge_elevation_profiles(
                                              spatial_graph_a.elevation_profile,
                                              spatial_graph_b.elevation_profile)
        merged_spatial_graph = SpatialGraph(merged_abstract_graph, pylon_cost,
                                            tube_cost, land_cost, latlngs,
                                            geospatials, elevation_profile)
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
        abstract.AbstractGraphsSets.__init__(self, spatial_edges_sets,
                            SpatialGraphsSet.init_from_spatial_edges_set,
                            SpatialGraphsSets.merge_two_spatial_graphs,
                            SpatialGraphsSet,
                            self.spatial_interpolator)

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
