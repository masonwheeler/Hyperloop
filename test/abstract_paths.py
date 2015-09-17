"""
Original Developer: Jonathan Ward
"""

class AbstractPath(object):
    def __init__(self, graph_physical_coordinates, interpolator,
                                                base_resolution):
        self.graph_coordinates = graph_physical_coordinates
        self.interpolator = interpolator
        self.path_coordinates, self.path_curvature = interpolator(
                          self.graph_coordinates, base_resolution)

    def to_plottable(self, color_string):
        """Return the physical coordinates of the path in a plottable format
        """
        physical_x_vals = [coord[0] for coord in self.path_coordinates]
        physical_y_vals = [coord[1] for coord in self.path_coordinates]
        path_points = [physical_x_vals, physical_y_vals]
        plottable_path = [path_points, color_string]
        return plottable_path

class AbstractPathsSet(object):
    def __init__(self, graphs_sets, interpolator, base_resolution,
                                                     path_builder):
        self.underlying_graphs = graphs_sets.selected_graphs
        self.paths = [path_builder(graph, interpolator, base_resolution)
                      for graph in self.underlying_graphs]

class AbstractPathsSets(object):
    def __init__(self, graphs_sets):
        pass
