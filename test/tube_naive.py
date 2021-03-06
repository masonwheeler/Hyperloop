"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import numpy as np
import scipy.signal

# Custom Modules:
import parameters
import smoothing_interpolate
import util


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

    def build_pylon(self):
        pylon = {"height" : self.pylon_height, 
                 "cost" : self.pylon_cost,
                 "latlng" : self.latlng.tolist()}
        return pylon

    def __init__(self, arc_length, land_elevation, tube_elevation, latlng):
        self.arc_length = arc_length
        self.land_elevation = land_elevation
        self.tube_elevation = tube_elevation
        self.latlng = latlng
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
        tube_coords_a = [tube_point_a.arc_length, tube_point_a.tube_elevation]
        tube_coords_b = [tube_point_b.arc_length, tube_point_b.tube_elevation]
        edge_vector = np.subtract(tube_coords_b, tube_coords_a)
        edge_length = np.linalg.norm(edge_vector)
        return edge_length

    def __init__(self, tube_point_a, tube_point_b):
        edge_length = self.compute_edge_length(tube_point_a, tube_point_b)
        self.tube_cost = self.compute_tube_cost(edge_length)
        self.tunneling_cost = self.compute_tunneling_cost(edge_length,
                                           tube_point_a, tube_point_b)


class NaiveTubeProfile(object):

    def compute_tube_elevations(self, arc_lengths, land_elevations, 
                                              peak_resolution=None):
        if peak_resolution == None:
            peak_resolution = 10
        land_elevation_peaks_indices_tuple = scipy.signal.argrelmax(
                             land_elevations, order=peak_resolution)
        land_elevation_peaks_indices = \
            land_elevation_peaks_indices_tuple[0].tolist()
        tube_elevations, tube_curvature_array = \
            smoothing_interpolate.bounded_curvature_extrema_interpolate(
             arc_lengths, land_elevations, land_elevation_peaks_indices,
                                      parameters.MAX_VERTICAL_CURVATURE)
        return [tube_elevations, tube_curvature_array]

    def build_pylons(self):
        pylons = [tube_point.build_pylon() for tube_point in self.tube_points]
        return pylons

    def __init__(self, elevation_profile, peak_resolution=None):
        arc_lengths = elevation_profile.arc_lengths        
        land_elevations = elevation_profile.land_elevations
        tube_elevations, tube_curvature_array = self.compute_tube_elevations(
                               arc_lengths, land_elevations, peak_resolution)
        latlngs = elevation_profile.latlngs
        tube_points = [TubePoint(arc_lengths[i], land_elevations[i],
                                     tube_elevations[i], latlngs[i]) 
                       for i in range(len(arc_lengths))]
        tube_edges = [TubeEdge(tube_points[i], tube_points[i + 1])
                      for i in range(len(tube_points) - 1)]
        tube_costs = [tube_edge.tube_cost for tube_edge in tube_edges]
        tunneling_costs = [tube_edge.tunneling_cost for tube_edge in tube_edges]
        pylons_costs = [tube_point.pylon_cost for tube_point in tube_points]
        self.arc_lengths = arc_lengths
        self.tube_points = tube_points
        self.land_elevations = land_elevations
        self.tube_elevations = tube_elevations
        self.tube_curvature_array = tube_curvature_array
        self.total_pylon_cost = sum(pylons_costs)
        self.tube_cost = sum(tube_costs)
        self.tunneling_cost = sum(tunneling_costs)
