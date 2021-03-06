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

import curvature
import reparametrize_speed


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
        pylon_at_tube_point = {"height": self.pylon_height,
                               "cost": self.pylon_cost,
                               "latlng": self.latlng}
        return pylon_at_tube_point

    def __init__(self, tube_elevation, land_elevation, latlng, geospatial):
        self.latlng = latlng
        self.geospatial = geospatial
        self.tube_elevation = tube_elevation
        self.land_elevation = land_elevation
        self.pylon_height = tube_elevation - land_elevation        
        self.is_underground = (self.pylon_height < 0)        
        self.pylon_cost = self.compute_pylon_cost()


class TubeEdge(object):

    def compute_tunneling_cost(self, edge_length, tube_point_a, tube_point_b):
        if tube_point_a.is_underground and tube_point_b.is_underground:
            tunneling_cost = (edge_length * 
                              parameters.TUNNELING_COST_PER_METER)
        if tube_point_a.is_underground and not tube_point_b.is_underground:
            tunneling_cost = (0.5 * edge_length * 
                              parameters.TUNNELING_COST_PER_METER)
        if not tube_point_a.is_underground and tube_point_b.is_underground:
            tunneling_cost = (0.5 * edge_length * 
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
        self.tunneling_cost = self.compute_tunneling_cost(edge_length,
                                           tube_point_a, tube_point_b)


class Tube(object):

    def build_tube_points(self, tube_profile):
        tube_points = []
        for i in range(len(self.tube_elevations)):
            tube_elevation = self.tube_elevations[i]
            land_elevation = self.land_elevations[i]
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

    def build_pylons(self):
        pylons = [tube_point.build_pylon_at_tube_point()
                  for tube_point in self.tube_points_with_pylons]
        return pylons

    def compute_pylons_cost(self):
        pylons_costs = [tube_point.pylon_cost for tube_point in
                        self.tube_points_with_pylons]
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
        self.arc_lengths = tube_profile.arc_lengths
        self.land_elevations = tube_profile.land_elevations
        self.tube_elevations = tube_profile.tube_elevations
        tube_points = self.build_tube_points(tube_profile)
        tube_edges = self.build_tube_edges(tube_points)  
        self.tube_points_with_pylons = self.select_tube_points_with_pylons(
            tube_points, tube_profile.tube_points_to_pylon_points_ratio)
        self.pylons_cost = self.compute_pylons_cost()
        self.tunneling_cost = self.compute_tunneling_cost(tube_edges)
        self.tube_cost = self.compute_tube_cost(tube_edges)        
        self.tube_curvature_array = tube_profile.tube_curvature_array

    def visualize(self):
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

        plottable_speeds_by_arc_length = \
            self.get_plottable_speeds_by_arc_length('c-')
        visualize.SPEED_PROFILE_PLOT_QUEUE.append(
                                  plottable_speeds_by_arc_length)
        are_speed_axes_equal = False
        visualize.plot_objects(visualize.SPEED_PROFILE_PLOT_QUEUE,
                                             are_speed_axes_equal)
        visualize.SPEED_PROFILE_PLOT_QUEUE.pop()

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
    
    def compute_speeds(self):
        self.speeds_by_arc_length = \
            curvature.vertical_curvature_array_to_max_allowed_vels(
                                             self.tube_curvature_array)
        self.constrained_speeds_by_arc_length = \
            reparametrize_speed.constrain_longitudinal_acceleration(
            speeds_by_arc_length, self.arc_lengths)
        self.speeds_by_time, self.cumulative_time_steps = \

    def get_plottable_speeds(self, color_string):
        speeds_by_arc_length = \
        speeds_by_arc_length_points = [self.arc_lengths,
                                       speeds_by_arc_length]  
        plottable_speeds_by_arc_length = [speeds_by_arc_length_points,
                                          color_string]
        
        
        return plottable_speeds_by_arc_length
    
