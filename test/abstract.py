"""
Original Developer: Jonathan Ward
Purpose of Module: To provide an interface for experimental Classes
Last Modified: 8/21/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Debugging
"""


# Custom Modules
import config
import math
import mergetree
import paretofront
import util

class AbstractGraph(object):

    def __init__(self, start_id, end_id, start_angle, end_angle, num_edges,
                 abstract_coords):
        self.start_id = start_id
        self.end_id = end_id
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.num_edges = num_edges
        self.abstract_coords = abstract_coords

    @classmethod
    def init_from_abstract_edge(cls, abstract_edge):
        start_id = abstract_edge.start_id
        end_id = abstract_edge.end_id
        start_angle = abstract_edge.angle
        end_angle = abstract_edge.angle
        num_edges = 1
        abstract_coords = [abstract_edge.start_abstract_coords,
                           abstract_edge.end_abstract_coords]
        data = cls(start_id, end_id, start_angle, end_angle, num_edges,
                                                       abstract_coords)
        return data

    @classmethod
    def init_from_abstract_graph(cls, abstract_graph):
        start_id = abstract_graph.start_id
        end_id = abstract_graph.end_id
        start_angle = abstract_graph.start_angle
        end_angle = abstract_graph.end_angle
        num_edges = abstract_graph.num_edges
        abstract_coords = abstract_graph.abstract_coords
        data = cls(start_id, end_id, start_angle, end_angle, num_edges,
                                                       abstract_coords)
        return data
    
    def init_from_abstract_graph_2(self, abstract_graph):
        start_id = abstract_graph.start_id
        end_id = abstract_graph.end_id
        start_angle = abstract_graph.start_angle
        end_angle = abstract_graph.end_angle
        num_edges = abstract_graph.num_edges
        abstract_coords = abstract_graph.abstract_coords
        self.__init__(start_id, end_id, start_angle, end_angle, num_edges,
                                                          abstract_coords)

    def build_local_lattice(self, lattice_coords, spacing):
        coord_pairs = util.to_pairs(lattice_coords)
        mid_points = map(util.get_midpoint, coord_pairs)
        slice_centers = [None] * (len(lattice_coords) + len(mid_points))
        slice_centers[::2] = lattice_coords
        slice_centers[1::2] = mid_points

        def slice_center_to_slice(slice_center):
            new_slice = [[slice_center[0], slice_center[1] - spacing]
                         [slice_center[0], slice_center[1]]
                         [slice_center[0], slice_center[1] + spacing]]
            return new_slice

        local_lattice = map(slice_center_to_slice, slice_centers)
        return local_lattice


class AbstractGraphsSet(object):

    def select_graphs(self, minimize_a_vals, minimize_b_vals):
        if self.graphs_a_b_vals == None:
            self.selected_graphs = self.unfiltered_graphs
        else:
            try:
                self.front = paretofront.ParetoFront(self.graphs_a_b_vals,
                                                     minimize_a_vals, minimize_b_vals)
                selected_graphs_indices = self.front.fronts_indices[-1]
                num_fronts = 1
                while (self.front.build_nextfront() and
                       num_fronts <= config.NUM_FRONTS):
                    num_fronts += 1
                    selected_graphs_indices += self.front.fronts_indices[-1]
                self.selected_graphs = [self.unfiltered_graphs[i] for i in
                                        selected_graphs_indices]
                return True
            except ValueError:
                self.selected_graphs = self.unfiltered_graphs
                return False

    def __init__(self, graphs, graphs_evaluator, graphs_num_edges,
                                minimize_a_vals, minimize_b_vals):
        self.unfiltered_graphs = graphs
        self.num_edges = graphs_num_edges
        self.graphs_a_b_vals = graphs_evaluator(graphs, graphs_num_edges)
        self.select_graphs(minimize_a_vals, minimize_b_vals)
        self.minimize_a_vals = minimize_a_vals
        self.minimize_b_vals = minimize_b_vals

    def update_graphs(self):
        """
        Update the selected graphs


        If the graphs are successfully updated return True, else return False.
        Update the graphs by adding the next front from the Pareto Frontier
        """
        if self.front == None:
            return False
        else:
            try:
                are_graphs_updated = self.front.build_nextfront()
            except ValueError:
                return False
            if are_graphs_updated:
                selected_graph_indices = self.front.fronts_indices[-1]
                for i in selected_graph_indices:
                    self.selected_graphs.append(self.unfiltered_graphs[i])
                return True
            else:
                return False


class AbstractGraphsSets(object):
    
    @staticmethod
    def graphs_set_updater(graphs_sets):
        graphs_sets.update_graphs()
        return graphs_sets

    def test_graph_pair_compatibility(self, graph_a, graph_b):
        graph_pair_compatible = (graph_a.end_id == graph_b.start_id and
          abs(graph_a.end_angle - graph_b.start_angle) < self.degree_constraint)
        return graph_pair_compatible

    def merge_two_graphs_sets(self, graphs_set_a, graphs_set_b):
        merged_graphs = []
        selected_a = graphs_set_a.selected_graphs
        selected_b = graphs_set_b.selected_graphs
        for graph_a in selected_a:
            for graph_b in selected_b:                
                if self.test_graph_pair_compatibility(graph_a, graph_b):
                    merged_graph = self.merge_graph_pair(graph_a, graph_b)
                    merged_graphs.append(merged_graph) 
        num_edges_a = graphs_set_a.num_edges
        num_edges_b = graphs_set_b.num_edges
        merged_num_edges = num_edges_a + num_edges_b
        if (len(merged_graphs) == 0):
            return None
        else:
            merged_graphs_set = self.graphs_set_builder(merged_graphs,
                                                        merged_num_edges)
            return merged_graphs_set

    def __init__(self, edges_sets, edges_set_to_graphs_set, merge_graph_pair,
                                                         graphs_set_builder):
        self.merge_graph_pair = merge_graph_pair
        self.graphs_set_builder = graphs_set_builder
        self.degree_constraint = edges_sets.degree_constraint
        base_graphs_sets = [edges_set_to_graphs_set(edges_set) for edges_set
                                              in edges_sets.final_edges_sets]
        graphs_sets_tree = mergetree.MasterTree(base_graphs_sets,
                                 self.merge_two_graphs_sets,
                                 AbstractGraphsSets.graphs_set_updater)
        root_graphs_set = graphs_sets_tree.root
        self.selected_graphs = root_graphs_set.selected_graphs


class AbstractPath(object):
    def __init__(self, graph_physical_coordinates, interpolator):
        self.graph_coordinates = graph_physical_coordinates
        self.interpolator = interpolator
        self.path_coordinates = interpolator(self.graph_coordinates)

class AbstractPathsSet(object):
    def __init__(self, graphs_set, spatial_interpolator, path_builder):
        self.spatial_paths = [path_builder(spatial_graph, spatial_interpolator)
                                 for spatial_graph in spatial_graphs_set.graphs]

