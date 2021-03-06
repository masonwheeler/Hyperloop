"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To provide an interface for the AbstractGraph class and related classes

Last Modified:
    8/21/15

Last Modified By:
    Jonathan Ward

Last Modification Purpose:
    Refactoring
"""

#Standard Modules
import numpy as np

# Custom Modules
import config
import mergetree
import paretofront
import util


class AbstractGraph(object):

    def __init__(self, start_id, end_id, start_angle, end_angle,
                               abstract_coords, physical_coords):
        self.start_id = start_id
        self.end_id = end_id
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.abstract_coords = abstract_coords
        self.physical_coords = physical_coords

    @classmethod
    def init_from_abstract_edge(cls, abstract_edge):
        start_id = abstract_edge.start_id
        end_id = abstract_edge.end_id
        start_angle = abstract_edge.angle
        end_angle = abstract_edge.angle
        abstract_coords = [abstract_edge.start_abstract_coords,
                           abstract_edge.end_abstract_coords]
        physical_coords = [abstract_edge.start_physical_coords,
                           abstract_edge.end_physical_coords]
        data = cls(start_id, end_id, start_angle, end_angle,
                           abstract_coords, physical_coords)
        return data

    @classmethod
    def merge_abstract_graphs(cls, abstract_graph_a, abstract_graph_b):
        start_id = abstract_graph_a.start_id
        end_id = abstract_graph_b.end_id
        start_angle = abstract_graph_a.start_angle
        end_angle = abstract_graph_b.end_angle
        abstract_coords = util.glue_list_pair(abstract_graph_a.abstract_coords,
                                              abstract_graph_b.abstract_coords)
        physical_coords = util.glue_list_pair(abstract_graph_a.physical_coords,
                                              abstract_graph_b.physical_coords)
        data = cls(start_id, end_id, start_angle, end_angle, 
                           abstract_coords, physical_coords)
        return data

    def to_plottable(self, color_string):
        physical_graph_points = zip(*self.physical_coords)
        plottable_graph = [physical_graph_points, color_string]
        return plottable_graph
"""
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
"""

class AbstractGraphsSet(object):

    def select_graphs(self, num_fronts_to_select):
        try:
            self.front = paretofront.ParetoFront(self.graphs_a_b_vals)
            selected_graphs_indices = self.front.front_indices
            current_num_fronts = 1
            while (self.front.build_next_front() and
                   current_num_fronts <= num_fronts_to_select):
                current_num_fronts += 1
                selected_graphs_indices = np.append(selected_graphs_indices, 
                                                   self.front.front_indices)
            return selected_graphs_indices
        except ValueError:
            print "encountered value error"
            self.front = None

    def __init__(self, graphs, graphs_evaluator, num_fronts_to_select,
                        graphs_num_edges, graph_filter_min_num_edges):
        self.graphs = graphs
        self.graphs_num_edges = graphs_num_edges
        self.graphs_a_b_vals = graphs_evaluator(graphs)
        if graphs_num_edges > graph_filter_min_num_edges:
            selected_graphs_indices = self.select_graphs(num_fronts_to_select)
            self.selected_graphs = [graphs[i] for i in selected_graphs_indices]
        else: 
            self.selected_graphs = graphs

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
                    self.selected_graphs.append(self.graphs[i])
                return True
            else:
                return False


class AbstractGraphsSets(object):
    
    @staticmethod
    def graphs_set_updater(graphs_sets):
        graphs_sets.update_graphs()
        return graphs_sets

    def test_graph_pair_compatibility(self, graph_a, graph_b):
        angle_difference = abs(graph_a.end_angle - graph_b.start_angle)
        angles_compatible = angle_difference < self.degree_constraint
        end_points_match = graph_a.end_id == graph_b.start_id
        graph_pair_compatible = (end_points_match and angles_compatible)
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
        if (len(merged_graphs) == 0):
            print "No graphs compatible"
            return None
        else:
            merged_graphs_num_edges = (graphs_set_a.graphs_num_edges +
                                       graphs_set_b.graphs_num_edges)
            merged_graphs_set = self.graphs_set_builder(merged_graphs,
                                                        merged_graphs_num_edges)
            return merged_graphs_set
    
    def __init__(self, edges_sets, edges_set_to_graphs_set, merge_graph_pair,
                                                          graphs_set_builder):
        self.merge_graph_pair = merge_graph_pair
        self.graphs_set_builder = graphs_set_builder
        self.degree_constraint = edges_sets.degree_constraint
        base_graphs_sets = [edges_set_to_graphs_set(edges_set)
                            for edges_set in edges_sets.filtered_edges_sets]
        graphs_sets_tree = mergetree.MasterTree(base_graphs_sets,
                                 self.merge_two_graphs_sets,
                                 AbstractGraphsSets.graphs_set_updater)
        root_graphs_set = graphs_sets_tree.root
        final_num_fronts_to_select = 1
        selected_graphs_indices = root_graphs_set.select_graphs(
                                         final_num_fronts_to_select)
        self.selected_graphs = [root_graphs_set.graphs[i] for i 
                                in selected_graphs_indices]

