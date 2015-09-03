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


class AbstractPoint:
    """Abstract object that represents a point.

    Attributes:
        point_id (int): Unique identifier for each point.
        lattice_x_coord (int): The x coordinate of the point with
                               relative to the lattice of points.
        lattice_y_coord (int): The y coordinate of the point with
                               relative to the lattice of points.
        spatial_x_coord (float): The x coordinate of the point in physical units.
        spatial_y_coord (float): The y coordinate of the point in physical units.

    """

    def __init__(self, point_id, lattice_x_coord, lattice_y_coord,
                 spatial_x_coord, spatial_y_coord):
        """
        Args:
            point_id (int): Unique identifier for each point.
            lattice_x_coord (int): The x coordinate of the point with
                                   relative to the lattice of points.
            lattice_y_coord (int): The y coordinate of the point with
                                   relative to the lattice of points.
            spatial_x_coord (float): The x coordinate of the point
                                    in physical units.
            spatial_y_coord (float): The y coordinate of the point
                                    in physical units.

        """
        self.point_id = point_id
        self.lattice_x_coord = lattice_x_coord
        self.lattice_y_coord = lattice_y_coord
        self.spatial_x_coord = spatial_x_coord
        self.spatial_ycoord = spatial_y_coord


class AbstractSlice(object):

    def __init__(self, lattice_x_coord, slice_bounds, start_id,
                                         slice_points_builder):
        self.points = slice_points_builder(lattice_x_coord, slice_bounds,
                                                                start_id)
        num_points = len(self.points)
        self.end_id = start_id + num_points


class AbstractLattice(object):

    def __init__(self, slices_bounds, slice_builder):
        self.slices = []
        start_id = 0
        lattice_x_coord = 0
        for slice_bounds in slices_bounds:
            new_slice = slice_builder(lattice_x_coord, slice_bounds, start_id)
            self.slices.append(new_slice.points)
            start_id = new_slice.end_id
            lattice_x_coord += 1


class AbstractEdge(object):

    def __init__(self, start_point, end_point):
        self.start_id = start_point.point_id
        self.end_id = end_point.point_id
        self.start_lattice_coords = [start_point.lattice_x_coord,
                                     start_point.lattice_y_coord]
        self.end_lattice_coords = [end_point.lattice_x_coord,
                                   end_point.lattice_y_coord]
        self.start_spatial_coords = [start_point.spatial_x_coord,
                                     start_point.spatial_y_coord]
        self.end_spatial_coords = [end_point.spatial_x_coord,
                                   end_point.spatial_y_coord]
        self.angle = math.degrees(math.atan2(
            end_point.spatial_y_coord - start_point.spatial_y_coord,
            end_point.spatial_x_coord - start_point.spatial_x_coord))
        self.is_useful = True


class AbstractEdgesSets(object):

    @staticmethod
    def is_edge_pair_compatible(edge_a, edge_b, degree_constraint):
        edge_pair_compatible = (edge_a.end_id == edge_b.start_id and
                                abs(edge_a.angle - edge_b.angle) < degree_constraint)
        return edge_pair_compatible

    def lattice_slices_to_unfiltered_edges_sets(self, lattice_slices,
                                                edge_builder):
        unfiltered_edges_sets = []
        for lattice_slice_index in range(len(lattice_slices) - 1):
            lattice_slice_a = lattice_slices[lattice_slice_index]
            lattice_slice_b = lattice_slices[lattice_slice_index + 1]
            edges_set = []
            for point_a in lattice_slice_a:
                for point_b in lattice_slice_b:
                    edges_set.append(edge_builder(point_a, point_b))
            unfiltered_edges_sets.append(edges_set)
        return unfiltered_edges_sets

    def determine_useful_edges(self, edges_sets, is_edge_pair_compatible):
        """Edge is useful if there are compatible adjacent edges"""
        for edge_a in edges_sets[0]:
            compatibles = [is_edge_pair_compatible(edge_a, edge_b)
                           for edge_b in edges_sets[1]]
            edge_a.is_useful = any(compatibles)
        for edge_set_index in range(1, len(edges_sets) - 1):
            for edge_b in edges_sets[edge_set_index]:
                compatibles_a = [is_edge_pair_compatible(edge_a, edge_b)
                                 for edge_a in edges_sets[edge_set_index - 1]]
                compatibles_c = [is_edge_pair_compatible(edge_b, edge_c)
                                 for edge_c in edges_sets[edge_set_index + 1]]
                edge_b.is_useful = any(compatibles_a) and any(compatibles_c)
        for edge_b in edges_sets[-1]:
            compatibles = [is_edge_pair_compatible(edge_a, edge_b)
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

    def iterative_filter(self, unfiltered_edges_sets, is_edge_pair_compatible):
        self.determine_useful_edges(unfiltered_edges_sets,
                                    is_edge_pair_compatible)
        prefilter_num_edges = util.list_of_lists_len(unfiltered_edges_sets)
        util.smart_print("The original number of edges: " +
                         str(prefilter_num_edges))
        filtered_edges_sets_list = []
        while True:
            self.determine_useful_edges(unfiltered_edges_sets,
                                        is_edge_pair_compatible)
            filtered_edges_sets = self.filter_edges(unfiltered_edges_sets)
            any_empty_edges_set = self.check_empty(filtered_edges_sets)
            if any_empty_edges_set:
                raise ValueError("Encountered Empty EdgesSet")
            postfilter_num_edges = util.list_of_lists_len(filtered_edges_sets)
            util.smart_print("The current number of edges: " +
                             str(postfilter_num_edges))
            filtered_edges_sets_list.append(filtered_edges_sets)
            if postfilter_num_edges == prefilter_num_edges:
                break
            prefilter_num_edges = postfilter_num_edges
        return filtered_edges_sets_list

    def __init__(self, lattice, edge_builder, is_edge_pair_compatible):
        lattice_slices = lattice.slices
        self.unfiltered_edges_sets = self.lattice_slices_to_unfiltered_edges_sets(
            lattice_slices, edge_builder)
        self.filtered_edges_sets_list = self.iterative_filter(
            self.unfiltered_edges_sets, is_edge_pair_compatible)
        self.final_edges_sets = self.filtered_edges_sets_list[-1]


class AbstractGraph(object):

    def __init__(self, start_id, end_id, start_angle, end_angle, num_edges,
                 lattice_coords):
        self.start_id = start_id
        self.end_id = end_id
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.num_edges = num_edges
        self.lattice_coords = lattice_coords

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

    @staticmethod
    def is_graph_pair_compatible(graph_a, graph_b, degree_constraint):
        graph_pair_compatible = (graph_a.end_id == graph_b.start_id and
            abs(graph_a.end_angle - graph_b.start_angle) < degree_constraint)
        return graph_pair_compatible

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

    def __init__(self, graphs, graphs_evaluator, is_graph_pair_compatible,
                 minimize_a_vals, minimize_b_vals, graphs_num_edges):
        self.unfiltered_graphs = graphs
        self.num_edges = graphs_num_edges
        self.graphs_a_b_vals = graphs_evaluator(graphs, graphs_num_edges)
        self.select_graphs(minimize_a_vals, minimize_b_vals)
        self.minimize_a_vals, self.minimize_b_vals = minimize_a_vals, minimize_b_vals
        self.is_graph_pair_compatible = is_graph_pair_compatible

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

    @staticmethod
    def merge_two_graphs_sets(graphs_set_a, graphs_set_b, is_graph_pair_compatible,
                              merge_two_graphs):
        merged_graphs = []
        selected_a = graphs_set_a.selected_graphs
        selected_b = graphs_set_b.selected_graphs
        for graph_a in selected_a:
            for graph_b in selected_b:
                if is_graph_pair_compatible(graph_a, graph_b):
                    merged_graphs.append(merge_two_graphs(graph_a, graph_b))
        return merged_graphs


def graphs_set_pair_merger(graphs_set_a, graphs_set_b, graphs_set_builder,
                           is_graph_pair_compatible, merge_two_graphs):
    merged_graphs = AbstractGraphsSet.merge_two_graphs_sets(graphs_set_a,
                                                            graphs_set_b, is_graph_pair_compatible, merge_two_graphs)
    num_edges_a = graphs_set_a.num_edges
    num_edges_b = graphs_set_b.num_edges
    merged_num_edges = num_edges_a + num_edges_b
    if (len(merged_graphs) == 0):
        return None
    else:
        merged_graphs_set = graphs_set_builder(merged_graphs, merged_num_edges)
        return merged_graphs_set


def graphs_set_updater(graphs_sets):
    graphs_sets.update_graphs()
    return graphs_sets
