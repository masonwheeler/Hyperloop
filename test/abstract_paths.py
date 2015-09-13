"""
Original Developer: Jonathan Ward
"""

class AbstractPath(object):
    def __init__(self, graph_physical_coordinates, interpolator):
        self.graph_coordinates = graph_physical_coordinates
        self.interpolator = interpolator
        self.path_coordinates = interpolator(self.graph_coordinates)

class AbstractPathsSet(object):
    def __init__(self, graphs_sets, interpolator, path_builder):
        self.spatial_paths = [path_builder(graph, interpolator)
                                for graph in graphs_sets.selected_graphs]

class AbstractPathsSets(object):
    def __init__(self, graphs_sets):
        pass