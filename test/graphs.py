"""
Original Developer: Jonathan Ward
Purpose of Module: To generate routes from the lattice edges and merge them.
Last Modified: 8/10/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Changed Class attributes to Instance attributes.
"""

import matplotlib.pyplot as plt

import abstract
import config
import util
import cacher
import visualize
import mergetree
import paretofront
import interpolate


class Graph:
    """Stores list of spatial points, their edge costs and curvature"""

    def compute_curvature(self):
        """Compute the curvature of an interpolation of the graph"""
        if self.num_edges > config.GRAPH_CURVATURE_MIN_NUM_EDGES:
            self.curvature_metric = interpolate.graph_curvature(
                self.geospatials, config.GRAPH_SAMPLE_SPACING)

    def __init__(self, num_edges, pylon_cost, land_cost, start_id, end_id,
                 start_angle, end_angle, latlngs, geospatials):
        self.num_edges = num_edges  # The number of edges in a graph
        self.pylon_cost = pylon_cost  # The total cost of the pylons
        self.land_cost = land_cost  # The total cost of the land acquired
        self.start_id = start_id  # The id of the start point in the graph
        self.end_id = end_id  # The id of the end point in the graph
        self.start_angle = start_angle  # The angle of the start edge in the graph
        self.end_angle = end_angle  # The angle of the end edge in the graph
        self.latlngs = latlngs  # The latitude longitude coordinates
        self.geospatials = geospatials  # The geospatial coordinates
        self.compute_curvature()

    def to_costcurvature_point(self):
        """Return the cost and curvature of the graph"""
        if self.num_edges > config.GRAPH_CURVATURE_MIN_NUM_EDGES:
            cost = self.pylon_cost + self.land_cost
            curvature = self.curvature_metric
            return [cost, curvature]

    def to_plottable(self, style):
        """Return the geospatial coords of the graph in plottable format"""
        plottable_graph = [zip(*self.geospatials), style]
        return plottable_graph

    def display(self):
        """display the cost and curvature of the graph"""
        print("This graph's land cost is: " + str(self.landcost) + ".")
        print("This graph's pylon cost is: " + str(self.start_angle) + ".")
        print("This graph's curvature is: " + str(self.curvature_metric) + ".")



class GraphsSet:
    """Stores all selected graphs between two given lattice slices"""
    minimize_cost = True
    minimize_curvature = True

    def graphs_to_costcurvaturepoints(self):
        """Compute cost and curvature of each graph with min number of edges"""
        if self.graphs_num_edges > config.GRAPH_CURVATURE_MIN_NUM_EDGES:
            self.cost_curvature_points = [graph.to_costcurvature_point()
                                          for graph in self.unfiltered_graphs]
        else:
            self.cost_curvature_points = None

    def select_graphs(self):
        """
        Select the Pareto optimal graphs, minimizing cost and curvature

        If the cost and curvature of the graphs have not been computed,
        then return all of the graphs.
        """
        if self.cost_curvature_points == None:
            self.selected_graphs = self.unfiltered_graphs
        else:
            try:
                self.front = paretofront.ParetoFront(
                    self.cost_curvature_points,
                    self.minimize_cost, self.minimize_curvature)
                selected_graphs_indices = self.front.fronts_indices[-1]
                values = [self.cost_curvature_points[i] for i
                          in selected_graphs_indices]
                num_fronts = 1
                while (self.front.build_nextfront() and
                       num_fronts <= config.NUM_FRONTS):
                    num_fronts += 1
                    selected_graphs_indices += self.front.fronts_indices[-1]
                self.selected_graphs = [self.unfiltered_graphs[i] for i in
                                        selected_graphs_indices]

                all_costs = [graph.land_cost + graph.pylon_cost for graph
                             in self.unfiltered_graphs]
                all_curvatures = [graph.curvature_metric for graph
                                  in self.unfiltered_graphs]
                selected_costs = [graph.land_cost + graph.pylon_cost for graph
                                  in self.selected_graphs]
                selected_curvatures = [graph.curvature_metric for graph
                                       in self.selected_graphs]
                """
                if config.VISUAL_MODE:
                    fig = plt.figure()
                    fig.suptitle('cost vs curvature tradeoff')
                    ax = fig.add_subplot(111)
                    ax.set_xlabel('cost in dollars')
                    ax.set_ylabel('curvature metric')
                    ax.plot(all_costs, all_curvatures, 'b.')
                    plt.show()
                    fig = plt.figure()
                    fig.suptitle('cost vs curvature tradeoff')
                    ax = fig.add_subplot(111)
                    ax.set_xlabel('cost in dollars')
                    ax.set_ylabel('curvature metric')
                    ax.plot(all_costs, all_curvatures, 'b.')
                    ax.plot(all_costs, all_curvatures, 'b.',
                             selected_costs, selected_curvatures, 'r.')
                    plt.show()
                """
            except ValueError:
                print("encountered ValueError")
                self.selected_graphs = self.unfiltered_graphs
                return 0

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

    def __init__(self, graphs):
        self.front = None
        self.unfiltered_graphs = graphs
        self.graphs_num_edges = self.unfiltered_graphs[0].num_edges
        self.graphs_to_costcurvaturepoints()
        self.select_graphs()


def graphs_set_updater(graphs_set):
    """Wrapper function to update a graphset"""
    is_graph_set_updated = graphs_set.update_graphs()
    return is_graph_set_updated


def edge_to_graph(edge):
    """Initializes a graph from an edge"""
    num_edges = 1
    pylon_cost = edge.pylon_cost
    land_cost = edge.land_cost
    start_id = edge.start_id
    end_id = edge.end_id
    start_angle = end_angle = edge.angle
    latlngs = edge.latlngs
    geospatials = edge.geospatials
    new_graph = Graph(num_edges, pylon_cost, land_cost, start_id, end_id,
                      start_angle, end_angle, latlngs, geospatials)
    return new_graph


def edges_set_to_graphs_set(edges_set):
    """Creates a GraphsSet from a set of edges"""
    graphs = map(edge_to_graph, edges_set)
    graphs_set = GraphsSet(graphs)
    return graphs_set


def edgessets_to_basegraphssets(edgessets):
    base_graph_sets = map(edges_set_to_graphs_set, edgessets)
    return base_graph_sets


def is_graph_pair_compatible(graph_a, graph_b):
    if (graph_a.end_id == graph_b.start_id):
        angle_difference = abs(graph_a.end_angle - graph_b.start_angle)
        if angle_difference < config.DEGREE_CONSTRAINT:
            return True
    return False


def merge_two_graphs(graph_a, graph_b):
    num_edges = graph_a.num_edges + graph_b.num_edges
    pylon_cost = graph_a.pylon_cost + graph_b.pylon_cost
    land_cost = graph_a.land_cost + graph_b.land_cost
    start_id = graph_a.start_id
    end_id = graph_b.end_id
    start_angle = graph_a.start_angle
    end_angle = graph_b.end_angle
    latlngs = util.smart_concat(graph_a.latlngs, graph_b.latlngs)
    geospatials = util.smart_concat(graph_a.geospatials, graph_b.geospatials)
    merged_graph = Graph(num_edges, pylon_cost, land_cost, start_id, end_id,
                         start_angle, end_angle, latlngs, geospatials)
    return merged_graph


def graphs_sets_merger(graphs_set_a, graphs_set_b):
    merged_graphs = []
    selected_a = graphs_set_a.selected_graphs
    selected_b = graphs_set_b.selected_graphs
    for graph_a in selected_a:
        for graph_b in selected_b:
            if is_graph_pair_compatible(graph_a, graph_b):
                merged_graph = merge_two_graphs(graph_a, graph_b)
                merged_graphs.append(merged_graph)
    if (len(merged_graphs) == 0):
        return None
    else:
        merged_graphs_set = GraphsSet(merged_graphs)
        return merged_graphs_set

def build_graphs(edgessets):
    base_graphs_sets = edgessets_to_basegraphssets(edgessets)
    graphs_sets_tree = mergetree.MasterTree(base_graphs_sets, graphs_sets_merger,
                                            graphs_set_updater)
    root_graphs_set = graphs_sets_tree.root
    selected_graphs = root_graphs_set.selected_graphs
    return selected_graphs


def get_graphs(edgessets):
    graphs = cacher.get_object("graphs", build_graphs, [edgessets],
                               config.GRAPHS_FLAG)
    return graphs


######### Spatial Graphs #########

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
        abstract.AbstractGraph.init_from_abstract_graph(abstract_graph)
        self.pylon_cost = pylon_cost  # The total cost of the pylons
        self.tube_cost = tube_cost
        self.land_cost = land_cost  # The total cost of the land acquired
        self.latlngs = latlngs  # The latitude longitude coordinates
        self.geospatials = geospatials  # The geospatial coordinates
        self.time = self.get_time(geospatials, num_edges)

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

    @classmethod
    def merge_two_spatial_graphs(cls, spatial_graph_a, spatial_graph_b):
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
    def is_spatial_graph_pair_compatible(spatial_graph_a, spatial_graph_b):
        graphs_compatible = abstract.AbstractGraphsSet.is_graph_pair_compatible(
            spatial_graph_a, spatial_graph_b, config.SPATIAL_DEGREE_CONSTRAINT)
        return graphs_compatible

    @staticmethod
    def spatial_graphs_cost_time(spatial_graphs, spatial_graphs_num_edges):
        if spatial_graphs_num_edges < config.GRAPH_FILTER_MIN_NUM_EDGES:
            return None
        else:
            spatial_graphs_cost_time = [spatial_graph.get_cost_time() for
                                        spatial_graph in spatial_graphs]
            return spatial_graphs_cost_time

    def __init__(self, spatial_graphs, spatial_graphs_length):
        minimize_cost = True
        minimize_time = True
        abstract.AbstractGraphsSet.__init__(self, spatial_graphs,
                                            spatial_graphs_length,
                                            self.spatial_graphs_cost_time,
                                    self.is_spatial_graph_pair_compatible,
                                            minimize_cost,
                                            minimize_time)

    @classmethod
    def init_from_spatial_edges_set(cls, spatial_edges_set):
        spatial_graphs = [SpatialGraph.init_from_spatial_edge(spatial_edge)
                                      for spatial_edge in spatial_edges_set]
        spatial_graphs_num_edges = 1
        return cls(spatial_graphs, spatial_graphs_num_edges)

def spatial_graphs_set_pair_merger(spatial_graphs_set_a, spatial_graphs_set_b):
    merged_spatial_graphs = abstract.graphs_set_pair_merger(
                                spatial_graphs_set_a,
                                spatial_graphs_set_b,
                                SpatialGraphsSet,
                            SpatialGraphsSet.is_spatial_graph_pair_compatible,
                                SpatialGraph.merge_two_spatial_graphs)
    return merged_spatial_graphs

def build_spatial_graphs(edges_sets):
    base_spatial_graphs_sets = [SpatialGraphsSet.init_from_spatial_edges_set(
                                edges_set) for edges_set in edges_sets]    
    spatial_graphs_sets_tree = mergetree.MasterTree(base_spatial_graphs_sets,
                                              spatial_graphs_set_pair_merger,
                                                 abstract.graphs_set_updater)
    root_spatial_graphs_set = spatial_graphs_sets_tree.root
    selected_spatial_graphs = root_spatial_graphs_set.selected_graphs
    return selected_spatial_graphs

