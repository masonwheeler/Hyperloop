"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import numpy as np

# Custom Modules:
import abstract_graphs
import curvature_constrain_speed
import mergetree
import parameters
import reparametrize_speed
import sample_path
import util


class TubeGraph(abstract_graphs.AbstractGraph):

    def compute_min_time(self, tube_curvature_array, arc_lengths):
        print "num arc lengths: " 
        print len(arc_lengths)
        print "num tube curvatures: " 
        print tube_curvature_array.size
        max_allowed_speeds = \
            curvature_constrain_speed.get_vertical_curvature_constrained_speeds(
                                                    tube_curvature_array)
        time_step_size = 1 #Second
        speeds_by_time, min_time = \
            reparametrize_speed.constrain_and_reparametrize_speeds(
                   max_allowed_speeds, arc_lengths, time_step_size)
        return min_time

    def fetch_min_time_and_total_cost(self):
        if self.min_time == None or self.total_cost == None:
            return None
        else: 
            min_time = round(self.min_time / 60.0, 3)
            total_cost = round(self.total_cost / 10.0**9, 3)
        return [min_time, total_cost]

    def __init__(self, abstract_graph, pylons_costs, total_pylon_cost,
                   tube_cost, tunneling_cost, total_cost, arc_lengths,
                           tube_elevations, tube_curvature_array=None):
        abstract_graphs.AbstractGraph.__init__(self, abstract_graph.start_id,
                                                       abstract_graph.end_id,
                                                  abstract_graph.start_angle,
                                                    abstract_graph.end_angle,
                                              abstract_graph.abstract_coords)
        self.pylons_costs = pylons_costs
        self.total_pylon_cost = total_pylon_cost
        self.tube_cost = tube_cost
        self.tunneling_cost = tunneling_cost
        self.total_cost = total_cost
        self.arc_lengths = arc_lengths
        self.tube_elevations = tube_elevations
        self.tube_curvature_array = tube_curvature_array
        if self.tube_curvature_array == None:
            self.min_time = None
        else:
            self.min_time = self.compute_min_time(tube_curvature_array,
                                                           arc_lengths)

    @classmethod
    def init_from_tube_edge(cls, tube_edge):
        abstract_edge = tube_edge.to_abstract_edge()
        abstract_graph = abstract_graphs.AbstractGraph.init_from_abstract_edge(
                                                                 abstract_edge)
        pylons_costs = tube_edge.pylons_costs
        total_pylon_cost = sum(pylons_costs)
        tube_cost = tube_edge.tube_cost
        tunneling_cost = tube_edge.tunneling_cost
        total_cost = total_pylon_cost + tube_cost + tunneling_cost
        arc_lengths = tube_edge.arc_lengths
        tube_elevations = tube_edge.tube_elevations
        data = cls(abstract_graph, pylons_costs, total_pylon_cost,
                   tube_cost, tunneling_cost, total_cost,
                   arc_lengths, tube_elevations)
        return data

    @staticmethod
    def merge_tube_curvature_arrays(tube_graph_a, tube_graph_b,
                                    graph_interpolator, resolution):
        boundary_arc_lengths_a = tube_graph_a.arc_lengths_partitions[-1]
        boundary_arc_lengths_b = tube_graph_b.arc_lengths_partitions[0]
        boundary_a_length = len(boundary_arc_lengths_a)
        boundary_b_length = len(boundary_arc_lengths_b)
        boundary_arc_lengths = util.offset_concat(boundary_arc_lengths_a,
                                                  boundary_arc_lengths_b)        
        boundary_tube_elevations_a = tube_graph_a.tube_elevations_partitions[-1]
        boundary_tube_elevations_b = tube_graph_b.tube_elevations_partitions[0]
        boundary_tube_elevations = util.smart_concat(boundary_tube_elevations_a,        
                                                     boundary_tube_elevations_b)
        boundary_points = zip(boundary_arc_lengths, boundary_tube_elevations)
        _, boundary_tube_curvature_array = graph_interpolator(boundary_points,
                                                              resolution)        
        boundary_tube_curvature_array_a = boundary_tube_curvature_array[
                                                         :boundary_a_length]
        boundary_tube_curvature_array_b = boundary_tube_curvature_array[
                                                         :boundary_b_length]        
        graph_a_tube_curvature_array = tube_graph_a.tube_curvature_array
        graph_b_tube_curvature_array = tube_graph_b.tube_curvature_array
        if (graph_a_tube_curvature_array == None and
            graph_b_tube_curvature_array == None):
            merged_curvature_array = boundary_tube_curvature_array_b
        elif (tube_graph_a.tube_curvature_array != None and
              tube_graph_b.tube_curvature_array != None):
            graph_a_tube_curvature_array = tube_graph_a.tube_curvature_array[
                                      -len(boundary_tube_curvature_array_a):]
            graph_b_tube_curvature_array = tube_graph_b.tube_curvature_array[
                                       :len(boundary_tube_curvature_array_b)]
            tube_curvature_array_a = np.maximum(graph_a_tube_curvature_array,
                                             boundary_tube_curvature_array_a)
            tube_curvature_array_b = np.maximum(graph_b_tube_curvature_array,
                                             boundary_tube_curvature_array_b)
            merged_curvature_array = util.smart_concat_array(
                                          tube_curvature_array_a,
                                          tube_curvature_array_b)
        elif (tube_graph_a.tube_curvature_array != None and
              tube_graph_b.tube_curvature_array == None):
            graph_a_tube_curvature_array = tube_graph_a.tube_curvature_array[
                                      -len(boundary_tube_curvature_array_a):]
            tube_curvature_array_a = np.maximum(graph_a_tube_curvature_array,
                                             boundary_tube_curvature_array_a)
            merged_curvature_array = util.smart_concat_array(
                tube_curvature_array_a, boundary_curvature_array_b)
        elif (tube_graph_a.tube_curvature_array == None and
              tube_graph_b.tube_curvature_array != None):
            graph_b_tube_curvature_array = tube_graph_b.tube_curvature_array[
                                       :len(boundary_tube_curvature_array_b)]
            tube_curvature_array_b = np.maximum(graph_b_tube_curvature_array,
                                             boundary_tube_curvature_array_b)
            merged_curvature_array = util.smart_concat_array(
                boundary_curvature_array_a, tube_curvature_array_b)
        return merged_curvature_array                

    @classmethod
    def merge_two_tube_graphs(cls, tube_graph_a, tube_graph_b, boundary_width,
                              graph_interpolator, resolution):
        abstract_graph_a = tube_graph_a.to_abstract_graph()
        abstract_graph_b = tube_graph_b.to_abstract_graph()
        merged_abstract_graph = \
            abstract_graphs.AbstractGraph.merge_abstract_graphs(
                                 abstract_graph_a, abstract_graph_b)
        pylons_costs = util.smart_concat(tube_graph_a.pylons_costs,
                                         tube_graph_b.pylons_costs)
        total_pylon_cost = sum(pylons_costs)
        tube_cost = tube_graph_a.tube_cost + tube_graph_b.tube_cost
        tunneling_cost = (tube_graph_a.tunneling_cost +
                          tube_graph_b.tunneling_cost)
        total_cost = tube_graph_a.total_cost + tube_graph_b.total_cost
        arc_lengths = util.offset_concat(tube_graph_a.arc_lengths, 
                                         tube_graph_b.arc_lengths)
        tube_elevations = util.smart_concat(tube_graph_a.tube_elevations,
                                            tube_graph_b.tube_elevations)
        merged_tube_curvature_array = TubeGraph.merge_tube_curvature_arrays(
                                 tube_graph_a, tube_graph_b, boundary_width,
                                             graph_interpolator, resolution)
        data = cls(merged_abstract_graph, pylons_costs, total_pylon_cost,
            tube_cost, tunneling_cost, total_cost, arc_lengths, tube_elevations,
                               tube_curvature_array=merged_tube_curvature_array)
        return data

    def to_abstract_graph(self):
        abstract_graph = abstract_graphs.AbstractGraph(self.start_id,
                                                       self.end_id,
                                                       self.start_angle,
                                                       self.end_angle,
                                                       self.abstract_coords)
        return abstract_graph


class TubeGraphsSet(abstract_graphs.AbstractGraphsSet):

    NUM_FRONTS_TO_SELECT = 3

    def get_tube_graphs_min_times_and_total_costs(self, tube_graphs):
        tube_graphs_min_times_and_total_costs = \
            [tube_graph.fetch_min_time_and_total_cost()
             for tube_graph in tube_graphs]
        if tube_graphs_min_times_and_total_costs[0] == None:
            return None
        else:
            return tube_graphs_min_times_and_total_costs

    def __init__(self, tube_graphs):
        minimize_cost = True
        minimize_time = True
        abstract_graphs.AbstractGraphsSet.__init__(self, tube_graphs,
                      self.get_tube_graphs_min_times_and_total_costs,
                                                       minimize_cost,
                                                       minimize_time,
                                           self.NUM_FRONTS_TO_SELECT)

    @classmethod
    def init_from_tube_edges_set(cls, tube_edges_set):
        tube_graphs = [TubeGraph.init_from_tube_edge(tube_edge)
                       for tube_edge in tube_edges_set]
        data = cls(tube_graphs)
        return data


class TubeGraphsSets(abstract_graphs.AbstractGraphsSets):

    def tube_graph_interpolator(self, waypoint_tube_elevations,
                                 waypoint_tube_arc_lengths):
        interpolated_tube_elevations, tube_curvature_array = \
            self.tube_interpolator(waypoint_tube_elevations,
                                   waypoint_tube_arc_lengths)
        return [interpolated_tube_elevations, tube_curvature_array]

    def merge_two_tube_graphs(self, tube_graph_a, tube_graph_b):
        merged_tube_graph = TubeGraph.merge_two_tube_graphs(tube_graph_a, 
                              tube_graph_b, self.tube_graph_interpolator,
                                          self.tube_elevation_resolution)
        return merged_tube_graph

    def __init__(self, tube_edges_sets, tube_interpolator,
                                tube_elevation_resolution):
        self.tube_interpolator = tube_interpolator
        self.tube_elevation_resolution = tube_elevation_resolution
        abstract_graphs.AbstractGraphsSets.__init__(self, tube_edges_sets,
                                   TubeGraphsSet.init_from_tube_edges_set,
                                               self.merge_two_tube_graphs,
                                                            TubeGraphsSet)
