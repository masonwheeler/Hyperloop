"""
Original Developer: Jonathan Ward
"""

#Custom Modules:
import config
import parameters
import tube_cost
import tunneling_cost
import util
import visualize

VISUALIZE_PROFILES = True

class TubePoint(object):

    def compute_pylon_cost(self, height_relative_to_ground):
        if self.is_underground:
            pylon_cost = 0
        else:
            height_cost = (height_relative_to_ground * \
                           parameters.PYLON_COST_PER_METER)
            base_cost = parameters.PYLON_BASE_COST
            pylon_cost = height_cost + base_cost
        return pylon_cost

    def __init__(self, height_relative_to_ground, latlng, geospatial):
        self.latlng = latlng
        self.geospatial = geospatial
        self.is_underground = (height_relative_to_ground < 0)        
        self.pylon_cost = self.compute_pylon_cost(height_relative_to_ground)

class TubeEdge(object):

    def compute_tunneling_cost(self, tube_point_a, tube_point_b):
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

    def compute_tube_cost(self):
        tube_cost = self.edge_length * parameters.TUBE_COST_PER_METER
        return tube_cost

    def __init__(self, tube_point_a, tube_point_b):
        

class Tube(object):

    def build_tube_points(tube_profile):
        tube_points_heights_relative_to_ground = util.subtract(
                                         tube_profile.tube_elevations,
                                         tube_profile.land_elevations)
        tube_points = []
        for i in range(len(tube_points_heights_relative_to_ground)):
            height = tube_points_heights_relative_to_ground[i]
            latlng = tube_profile.latlngs[i]
            geospatial = tube_profile.geospatials[i]
            tube_point = TubePoint(height, latlng, geospatial)
            tube_points.append(tube_point)
        return tube_points
        
    def build_tube_edges(tube_points):
        tube_points_pairs = util.to_pairs(tube_points)
        tube_edges = [TubeEdge(pair[0], pair[1]) for pair in tube_points_pairs]
        return tube_edges

    def build_pylons(self):
        self.pylon_heights = util.subtract(tube_profile.tube_elevations,
                                           tube_profile.land_elevations)
        pylon_costs = [pylon_cost.compute_pylon_cost_v1(pylon_height)
                       for pylon_height in self.pylon_heights]
        self.pylons = [{"latlng" : self.latlngs[i],
                        "landElevation" : self.land_elevations[i],
                        "pylonHeight" : self.pylon_heights[i],
                        "pylonCost" : pylon_costs[i]}
                        for i in range(len(self.pylon_heights))]
        self.pylon_cost = sum(pylon_costs)

    def compute_tunneling_cost(self):

    def compute_tube_cost(self):
        geospatial_x_vals, geospatial_y_vals = zip(*self.geospatials)
        tube_coords = zip(geospatial_x_vals, geospatial_y_vals, tube_elevations)
        self.tube_cost = tube_cost.compute_tube_cost_v1(self.tube_coords)

    def __init__(self, tube_profile):
        self.compute_tube_cost(tube_profile)
        self.compute_tunneling_cost(tube_profile)
        self.build_pylons(tube_profile)
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

