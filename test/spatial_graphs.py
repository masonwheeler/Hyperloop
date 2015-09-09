"""
Original Developer: Jonathan Ward
Purpose of Module: To generate routes from the lattice edges and merge them.
Last Modified: 8/10/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Changed Class attributes to Instance attributes.
"""

import matplotlib.pyplot as plt

import abstract_graphs as abstract
import config
import util
import cacher
import visualize
import mergetree
import paretofront
import interpolate

class SpatialGraph(abstract.AbstractGraph):
    """Stores list of spatial points, their edge costs and curvature"""

    def get_time(self, geospatials, num_edges):
        """Compute the curvature of an interpolation of the graph"""
        if num_edges > config.GRAPH_FILTER_MIN_NUM_EDGES:
            time = interpolate.graph_curvature(
                self.geospatials, config.GRAPH_SAMPLE_SPACING)
            return time

    def __init__(self, abstract_graph, pylon_cost, tube_cost, land_cost,
                                                 latlngs, geospatials):
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
        self.time = self.get_time(geospatials, self.num_edges)

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
        data = cls(abstract_graph, pylon_cost, tube_cost, land_cost,
                                               latlngs, geospatials)
        return data

    def to_abstract_graph(self):
        abstract_graph = abstract.AbstractGraph(self.start_id,
                                                self.end_id,
                                                self.start_angle,
                                                self.end_angle,
                                                self.num_edges,
                                                self.abstract_coords)
        return abstract_graph

    @classmethod
    def merge_two_spatial_graphs(cls, spatial_graph_a, spatial_graph_b):
        #print("merged two spatial graphs")
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
        data = cls(merged_abstract_graph, pylon_cost, tube_cost, land_cost,
                                                      latlngs, geospatials)
        return data
         
    def get_total_cost(self):
        return self.pylon_cost + self.tube_cost + self.land_cost

    def to_plottable(self, style):
        """Return the geospatial coords of the graph in plottable format"""
        plottable_graph = [zip(*self.geospatials), style]
        return plottable_graph


class SpatialGraphsSet(abstract.AbstractGraphsSet):

    @staticmethod
    def spatial_graphs_cost_time(spatial_graphs, spatial_graphs_num_edges):
        if spatial_graphs_num_edges < config.GRAPH_FILTER_MIN_NUM_EDGES:
            return None
        else:
            spatial_graphs_cost_time = [spatial_graph.get_cost_time() for
                                        spatial_graph in spatial_graphs]
            return spatial_graphs_cost_time

    def __init__(self, spatial_graphs, spatial_graphs_num_edges):
        minimize_cost = True
        minimize_time = True
        abstract.AbstractGraphsSet.__init__(self, spatial_graphs,
                                            spatial_graphs_num_edges,
                                            self.spatial_graphs_cost_time,
                                            minimize_cost,
                                            minimize_time)

    @classmethod
    def init_from_spatial_edges_set(cls, spatial_edges_set):
        spatial_graphs = [SpatialGraph.init_from_spatial_edge(spatial_edge)
                                      for spatial_edge in spatial_edges_set]
        spatial_graphs_num_edges = 1
        return cls(spatial_graphs, spatial_graphs_num_edges)


class SpatialGraphsSets(abstract.AbstractGraphsSets):
    
    def __init__(self, spatial_edges_sets):
        abstract.AbstractGraphsSets.__init__(self, spatial_edges_sets,
                            SpatialGraphsSet.init_from_spatial_edges_set,
                            SpatialGraph.merge_two_spatial_graphs,
                            SpatialGraphsSet)
    

