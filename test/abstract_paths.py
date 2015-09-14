"""
Original Developer: Jonathan Ward
"""

class AbstractPath(object):
    def __init__(self, graph_physical_coordinates, interpolator):
        self.graph_coordinates = graph_physical_coordinates
        self.interpolator = interpolator
        self.path_coordinates = interpolator(self.graph_coordinates)

    def to_plottable(self, color_string):
        """Return the physical coordinates of the path in a plottable format
        """
        physical_x_vals = [coord[0] for coord in self.path_coordinates]
        physical_y_vals = [coord[1] for coord in self.path_coordinates]
        path_points = [physical_x_vals, physical_y_vals]
        plottable_path = [path_points, color_string]
        return plottable_path

class AbstractPathsSet(object):
    def __init__(self, graphs_sets, interpolator, path_builder):
        self.spatial_paths = [path_builder(graph, interpolator)
                                for graph in graphs_sets.selected_graphs]

class AbstractPathsSets(object):
    def __init__(self, graphs_sets):
        pass
