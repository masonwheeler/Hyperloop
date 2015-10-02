"""
Original Developer: Jonathan Ward
"""

#Standard Modules:
import numpy as np

#Custom Modules:
import config
import parameters
import util
import visualize


VISUALIZE_PROFILES = True


class Pylon(object):
    
    def __init__(self, pylon_height, pylon_cost, latlng):
        self.pylon_height = pylon_height
        self.pylon_cost = pylon_cost 
        self.latlng = latlng


class TubePoint(object):

    def compute_pylon_cost(self):
        if self.is_underground:
            pylon_cost = 0
        else:
            height_cost = (self.pylon_height * 
                           parameters.PYLON_COST_PER_METER)
            base_cost = parameters.PYLON_BASE_COST
            pylon_cost = height_cost + base_cost
        return pylon_cost

    def build_pylon_at_tube_point(self):
        pylon_at_tube_point = Pylon(self.pylon_height,
                                    self.pylon_cost,
                                    self.latlng)
        return pylon_at_tube_point

    def __init__(self, tube_elevation, land_elevation, latlng, geospatial):
        self.latlng = latlng
        self.geospatial = geospatial
        self.pylon_height = tube_elevation - land_elevation
        self.is_underground = (self.pylon_height < 0)        
        self.pylon_cost = self.compute_pylon_cost()


class TubeEdge(object):

    def compute_tunneling_cost(self, edge_length, tube_point_a, tube_point_b):
        if tube_point_a.is_underground and tube_point_b.is_underground:
            tunneling_cost = (self.edge_length * \
                              parameters.TUNNELING_COST_PER_METER)
        if tube_point_a.is_underground and not tube_point_b.is_underground:
            tunneling_cost = (0.5 * self.edge_length * 
                              parameters.TUNNELING_COST_PER_METER)
        if not tube_point_a.is_underground and tube_point_b.is_underground:
            tunneling_cost = (0.5 * self.edge_length * 
                              parameters.TUNNELING_COST_PER_METER)
        if not tube_point_a.is_underground and not tube_point_b.is_underground:
            tunneling_cost = 0.0
        return tunneling_cost

    def compute_tube_cost(self, edge_length):
        tube_cost = edge_length * parameters.TUBE_COST_PER_METER
        return tube_cost

    def compute_edge_length(self, tube_point_a, tube_point_b):
        tube_coords_a = [tube_point_a.geospatial[0], tube_point_b.geospatial[1],
                         tube_point_a.tube_elevation]
        tube_coords_b = [tube_point_b.geospatial[0], tube_point_b.geospatial[1],
                         tube_point_b.tube_elevation]
        edge_vector = util.subtract(tube_coords_a, tube_coords_b)
        edge_length = np.linalg.norm(edge_vector)
        return edge_length

    def __init__(self, tube_point_a, tube_point_b):
        edge_length = self.compute_edge_length(tube_point_a, tube_point_b)
        self.tube_cost = self.compute_tube_cost(edge_length)
        self.tunneling_cost = self.compute_tunneling_cost(edge_length)


class Tube(object):

    def build_tube_points(self, tube_profile):
        tube_points = []
        for i in range(len(tube_profile.tube_elevations)):
            tube_elevation = tube_profile.tube_elevations[i]
            land_elevation = tube_profile.land_elevations[i]
            latlng = tube_profile.latlngs[i]
            geospatial = tube_profile.geospatials[i]
            tube_point = TubePoint(tube_elevation, land_elevation,
                                               latlng, geospatial)
            tube_points.append(tube_point)
        return tube_points
        
    def build_tube_edges(self, tube_points):
        tube_points_pairs = util.to_pairs(tube_points)
        tube_edges = [TubeEdge(pair[0], pair[1]) for pair in tube_points_pairs]
        return tube_edges

    def select_tube_points_with_pylons(self, tube_points,
                                             tube_points_to_pylon_points_ratio):
        tube_points_with_pylons = tube_points[::
                                  tube_points_to_pylon_points_ratio]
        return tube_points_with_pylons

    def build_pylons(self, tube_points_with_pylons):
        pylons = [tube_point.build_pylon_at_tube_point()
                  for tube_point in tube_points_with_pylons]
        return pylons

    def compute_pylons_cost(self, tube_points_with_pylons):
        pylons_costs = [tube_point.pylon_cost for tube_point in
                        tube_points_with_pylons]
        pylons_cost = sum(pylons_costs)
        return pylons_cost

    def compute_tunneling_cost(self, tube_edges):
        tunneling_costs = [tube_edge.tunneling_cost for tube_edge in tube_edges]
        tunneling_cost = sum(tunneling_costs)
        return tunneling_cost

    def compute_tube_cost(self, tube_edges):
        tube_costs = [tube_edge.tube_cost for tube_edge in tube_edges]
        tube_cost = sum(tube_costs)
        return tube_cost

    def __init__(self, tube_profile):
        tube_points = self.build_tube_points(tube_profile)
        tube_edges = self.build_tube_edges(tube_points)  
        tube_points_with_pylons = self.select_tube_points_with_pylons(
                           tube_profile.tube_points_to_pylon_points_ratio)
        self.pylons_cost = self.compute_pylons_cost(tube_points_with_pylons)
        self.tunneling_cost = self.compute_tunneling_cost(tube_edges)
        self.tube_cost = self.compute_tube_cost(tube_edges)

    def visualize_tube(self, tube_profile):
        if VISUALIZE_PROFILES and config.VISUAL_MODE:
            plottable_tube_profile = self.get_plottable_tube_profile('r-')
            visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                                       plottable_tube_profile)
            plottable_land_profile = self.get_plottable_land_profile('b-')
            visualize.ELEVATION_PROFILE_PLOT_QUEUE.append(
                                       plottable_land_profile)
            are_elevation_axes_equal = False
            visualize.plot_objects(visualize.ELEVATION_PROFILE_PLOT_QUEUE,
                                                 are_elevation_axes_equal)
            visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()
            visualize.ELEVATION_PROFILE_PLOT_QUEUE.pop()

            plottable_tube_curvature = self.get_plottable_tube_curvature('g-')
            visualize.CURVATURE_PROFILE_PLOT_QUEUE.append(
                                        plottable_tube_curvature)
            are_curvature_axes_equal = False
            visualize.plot_objects(visualize.CURVATURE_PROFILE_PLOT_QUEUE,
                                                 are_curvature_axes_equal)
            visualize.CURVATURE_PROFILE_PLOT_QUEUE.pop()

    def get_plottable_tube_profile(self, color_string):
        tube_profile_points = [self.arc_lengths, self.tube_elevations]
        plottable_tube_profile = [tube_profile_points, color_string]
        return plottable_tube_profile

    def get_plottable_land_profile(self, color_string):
        land_profile_points = [self.arc_lengths, self.land_elevations]
        plottable_land_profile = [land_profile_points, color_string]
        return plottable_land_profile

    def get_plottable_tube_curvature(self, color_string):
        tube_curvature_points = [self.arc_lengths, self.tube_curvature_array]
        plottable_tube_curvature = [tube_curvature_points, color_string]
        return plottable_tube_curvature

