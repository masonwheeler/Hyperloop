"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To provide an interface for the AbstractEdgesSets class and related classes

Last Modified:
    09/08/15

Last Modified By:
    Jonathan Ward

Last Modification Purpose:
    Created Module
"""

# Standard Modules:
import math

# Custom Modules:
import util


class AbstractEdge(object):

    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point
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

    def to_plottable_edge(self, color_string):
        plottable_points = zip(self.start_physical_coords,
                               self.end_physical_coords)
        plottable_edge = [plottable_points, color_string]
        return plottable_edge        


class AbstractEdgesSets(object):

    def is_edge_pair_compatible(self, edge_a, edge_b):
        do_end_points_match = edge_a.end_id == edge_b.start_id
        are_angles_compatible = (abs(edge_a.angle - edge_b.angle)
                                 < self.degree_constraint)
        edge_pair_compatible = do_end_points_match and are_angles_compatible
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
            current_edge_set = edges_sets[edge_set_index]
            last_edge_set = edges_sets[edge_set_index - 1]
            next_edge_set = edges_sets[edge_set_index + 1]
            for edge_b in current_edge_set:                
                compatibles_a = [self.is_edge_pair_compatible(edge_a, edge_b)
                                 for edge_a in last_edge_set]
                compatibles_c = [self.is_edge_pair_compatible(edge_b, edge_c)
                                 for edge_c in next_edge_set]
                edge_b.is_useful = any(compatibles_a) and any(compatibles_c)
        for edge_b in edges_sets[-1]:
            compatibles = [self.is_edge_pair_compatible(edge_a, edge_b)
                           for edge_a in edges_sets[-2]]
            edge_b.is_useful = any(compatibles)

    def filter_edges(self, edges_sets):
        unfiltered_length = 0
        filtered_length = 0
        filtered_edges_sets = []
        for edges_set in edges_sets:
            filtered_edges_set = []
            for edge in edges_set:
                if edge.is_useful:
                    filtered_edges_set.append(edge)
            unfiltered_length += len(edges_set)
            filtered_length += len(filtered_edges_set)
            filtered_edges_sets.append(filtered_edges_set)
        return filtered_edges_sets

    def check_empty(self, edges_sets):
        for edges_set in edges_sets:
            if len(edges_set) == 0:
                return True
        return False

    def iterative_filter(self, edges_sets):
        edges_sets = self.filter_edges(edges_sets)
        prefilter_num_edges = util.list_of_lists_len(edges_sets)
        util.smart_print("The original number of edges: " +
                         str(prefilter_num_edges))
        while True:
            self.determine_useful_edges(edges_sets)
            edges_sets = self.filter_edges(edges_sets)
            any_empty_edges_set = self.check_empty(edges_sets)
            if any_empty_edges_set:
                raise ValueError("Encountered Empty EdgesSet")
            postfilter_num_edges = util.list_of_lists_len(edges_sets)
            if postfilter_num_edges == prefilter_num_edges:
                util.smart_print("The final number of edges is: " +
                             str(postfilter_num_edges))
                break
            util.smart_print("The current number of edges is: " +
                             str(postfilter_num_edges))
            prefilter_num_edges = postfilter_num_edges
        return edges_sets

    def __init__(self, lattice, edge_builder, degree_constraint):
        self.degree_constraint = degree_constraint
        self.raw_edges_sets = self.lattice_slices_to_unfiltered_edges_sets(
            lattice.slices, edge_builder)

    def get_plottable_edges(self, color_string):
        plottable_edges = []
        for edges_set in self.filtered_edges_sets:
            for edge in edges_set:
                plottable_edge = edge.to_plottable_edge(color_string)
                plottable_edges.append(plottable_edge)
        return plottable_edges

