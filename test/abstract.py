"""
Original Developer: Jonathan Ward
Purpose of Module: To provide an interface for experimental Classes
Last Modified: 8/21/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Debugging
"""

# Standard Modules
import numpy as np

# Custom Modules
import config
import math
import mergetree
import paretofront
import util


class AbstractPoint(object):
    """Abstract object that represents a point.

    Attributes:
        point_id (int): Unique identifier for each point.
        abstract_x_coord (int): The x coordinate of the point with
                               relative to the lattice of points.
        abstract_y_coord (int): The y coordinate of the point with
                               relative to the lattice of points.
        physical_x_coord (float): The x coordinate of the point
                                in physical units.
        physical_y_coord (float): The y coordinate of the point
                                in physical units.

    """

    def __init__(self, point_id, abstract_x_coord, abstract_y_coord,
                 physical_x_coord, physical_y_coord):
        self.point_id = point_id
        self.abstract_x_coord = abstract_x_coord
        self.abstract_y_coord = abstract_y_coord
        self.physical_x_coord = physical_x_coord
        self.physical_y_coord = physical_y_coord

class AbstractSlice(object):

    def __init__(self, abstract_x_coord, slice_bounds, start_id,
                                         slice_points_builder):
        self.points, self.end_id = slice_points_builder(abstract_x_coord,
                                                 slice_bounds, start_id)
    
    def get_physical_x_coords(self):
        physical_x_coords = [point.physical_x_coord for point in self.points]
        return physical_x_coords
    
    def get_physical_y_coords(self):
        physical_y_coords = [point.physical_y_coord for point in self.points]
        return physical_y_coords

class AbstractLattice(object):

    def __init__(self, slices_bounds, slice_builder):
        self.slices = []
        start_id = 0
        lattice_x_coord = 0
        for slice_bounds in slices_bounds:
            new_slice = slice_builder(lattice_x_coord, slice_bounds, start_id)
            self.slices.append(new_slice)
            start_id = new_slice.end_id
            lattice_x_coord += 1

    def get_plottable_lattice(self):
        slices_physical_x_coords = [eachSlice.get_physical_x_coords()
                                    for eachSlice in self.slices]        
        slices_physical_y_coords = [eachSlice.get_physical_y_coords()
                                    for eachSlice in self.slices]
        physical_x_coords = util.fast_concat(slices_physical_x_coords)
        physical_y_coords = util.fast_concat(slices_physical_y_coords)
        physical_x_coords_array = np.array(physical_x_coords)
        physical_y_coords_array = np.array(physical_y_coords)
        return [physical_x_coords_array, physical_y_coords_array]        


class AbstractEdge(object):

    def __init__(self, start_point, end_point):
        self.start_id = start_point.point_id        
        self.end_id = end_point.point_id
        self.start_abstract_coords = [start_point.abstract_x_coord,
                                      start_point.abstract_y_coord]
        self.end_abstract_coords = [end_point.abstract_x_coord,
                                    end_point.abstract_y_coord]
        self.start_physical_coords = [start_point.physical_x_coord,
                                     start_point.physical_y_coord]
        self.end_physical_coords = [end_point.physical_x_coord,
                                   end_point.physical_y_coord]
        self.angle = math.degrees(math.atan2(
            end_point.physical_y_coord - start_point.physical_y_coord,
            end_point.physical_x_coord - start_point.physical_x_coord))
        self.is_useful = True


class AbstractEdgesSets(object):

    def is_edge_pair_compatible(self, edge_a, edge_b):
        edge_pair_compatible = (edge_a.end_id == edge_b.start_id and
            abs(edge_a.angle - edge_b.angle) < self.degree_constraint)
        return edge_pair_compatible

    def lattice_slices_to_unfiltered_edges_sets(self, lattice_slices,
                                                       edge_builder):
        unfiltered_edges_sets = []
        for lattice_slice_index in range(len(lattice_slices) - 1):
            lattice_slice_a = lattice_slices[lattice_slice_index]
            lattice_slice_b = lattice_slices[lattice_slice_index + 1]
            edges_set = []
            for point_a in lattice_slice_a.points:
                for point_b in lattice_slice_b.points:
                    new_edge = edge_builder(point_a, point_b)                    
                    edges_set.append(new_edge)
            unfiltered_edges_sets.append(edges_set)
        return unfiltered_edges_sets

    def determine_useful_edges(self, edges_sets):
        """Edge is useful if there are compatible adjacent edges"""
        for edge_a in edges_sets[0]:
            compatibles = [self.is_edge_pair_compatible(edge_a, edge_b)
                           for edge_b in edges_sets[1]]
            edge_a.is_useful = any(compatibles)
        for edge_set_index in range(1, len(edges_sets) - 1):
            for edge_b in edges_sets[edge_set_index]:
                compatibles_a = [self.is_edge_pair_compatible(edge_a, edge_b)
                                 for edge_a in edges_sets[edge_set_index - 1]]
                compatibles_c = [self.is_edge_pair_compatible(edge_b, edge_c)
                                 for edge_c in edges_sets[edge_set_index + 1]]
                edge_b.is_useful = any(compatibles_a) and any(compatibles_c)
        for edge_b in edges_sets[-1]:
            compatibles = [self.is_edge_pair_compatible(edge_a, edge_b)
                           for edge_a in edges_sets[-2]]
            edge_b.is_useful = any(compatibles)

    def filter_edges(self, edges_sets):
        filtered_edges_sets = []
        for edges_set in edges_sets:
            filtered_edges_set = []
            for edge in edges_set:
                if edge.is_useful:
                    filtered_edges_set.append(edge)
            filtered_edges_sets.append(filtered_edges_set)
        return filtered_edges_sets

    def check_empty(self, edges_sets):
        for edges_set in edges_sets:
            if len(edges_set) == 0:
                return True
        return False

    def iterative_filter(self, unfiltered_edges_sets):
        prefilter_num_edges = util.list_of_lists_len(unfiltered_edges_sets)
        util.smart_print("The original number of edges: " +
                         str(prefilter_num_edges))
        filtered_edges_sets_list = []
        while True:
            self.determine_useful_edges(unfiltered_edges_sets)
            filtered_edges_sets = self.filter_edges(unfiltered_edges_sets)
            any_empty_edges_set = self.check_empty(filtered_edges_sets)
            if any_empty_edges_set:
                raise ValueError("Encountered Empty EdgesSet")
            filtered_edges_sets_list.append(filtered_edges_sets)
            postfilter_num_edges = util.list_of_lists_len(filtered_edges_sets)
            if postfilter_num_edges == prefilter_num_edges:
                util.smart_print("The final number of edges is: " +
                             str(postfilter_num_edges))
                break
            util.smart_print("The current number of edges is: " +
                             str(postfilter_num_edges))
            prefilter_num_edges = postfilter_num_edges
        return filtered_edges_sets_list

    def __init__(self, lattice, edge_builder, degree_constraint):
        self.degree_constraint = degree_constraint
        self.unfiltered_edges_sets = self.lattice_slices_to_unfiltered_edges_sets(
            lattice.slices, edge_builder)
        self.filtered_edges_sets_list = self.iterative_filter(
                                       self.unfiltered_edges_sets)
        self.final_edges_sets = self.filtered_edges_sets_list[-1]


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

