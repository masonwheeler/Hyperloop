"""
Original Developer: Jonathan Ward
Purpose of Module: To build edges with associated cost and elevation data
                   from pairs of lattice points.
Last Modified: 8/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To test out pylonsv2
"""

# Standard Modules:
import math
import time

# Our Modules
import abstract
import cacher
import config
import curvature
import elevation
import interpolate
import landcover
import parameters
import proj
import tube
import util
import visualize

class SpatialEdge(abstract.AbstractEdge):

    @staticmethod
    def get_geospatials(start_spatial_point, end_spatial_point):
        geospatials = [start_spatial_point.geospatial,
                         end_spatial_point.geospatial]
        return geospatials

    @staticmethod
    def get_latlngs(start_spatial_point, end_spatial_point):
        latlngs = [start_spatial_point.latlng,  
                     end_spatial_point.latlng]
        return latlngs

    @staticmethod
    def compute_land_cost(edge_is_in_right_of_way, geospatials):
        if edge_is_in_right_of_way:
            land_cost = parameters.RIGHT_OF_WAY_LAND_COST
        else:
            start_geospatial, end_geospatial = geospatials
            landcover_geospatials, distances = util.build_grid(
                start_geospatial, end_geospatial, config.LAND_POINT_SPACING)
            landcover_lat_lngs = proj.geospatials_to_latlngs(landcover_geospatials,
                                                             config.PROJ)
            landcover_cost_densities = landcover.get_landcover_cost_densities(
                                                           landcover_lat_lngs)
            land_cost = landcover.cost_densities_to_landcost(
                                    landcover_cost_densities)
        return land_cost

    @staticmethod
    def get_elevation_profile(geospatials):
        start_geospatial, end_geospatial = geospatials
        geospatials_grid, distances = util.build_grid(start_geospatial,
                              end_geospatial, parameters.PYLON_SPACING)        
        elevation_profile = elevation.get_elevation_profile(geospatials_grid,
                                                            distances)
        return elevation_profile

    @staticmethod
    def compute_pylon_cost_and_tube_cost(elevation_profile):
        tube_cost, pylon_cost, tube_elevations = tube.quick_build_tube_v1(
                                                            elevation_profile)
        return [pylon_cost, tube_cost]
            
    def __init__(self, start_spatial_point, end_spatial_point):
        abstract.AbstractEdge.__init__(self, start_spatial_point,
                                               end_spatial_point)
        self.start_spatial_point = start_spatial_point
        self.end_spatial_point = end_spatial_point
        self.geospatials = SpatialEdge.get_geospatials(start_spatial_point,
                                                         end_spatial_point)
        elevation_profile = SpatialEdge.get_elevation_profile(self.geospatials)
        self.latlngs = SpatialEdge.get_latlngs(start_spatial_point,
                                                 end_spatial_point)
        self.elevation_profile = SpatialEdge.get_elevation_profile(
                                                      self.geospatials)
        edge_is_in_right_of_way = (start_spatial_point.is_in_right_of_way and
                                     end_spatial_point.is_in_right_of_way)
        self.land_cost = SpatialEdge.compute_land_cost(edge_is_in_right_of_way,
                                                       self.geospatials)
        self.pylon_cost, self.tube_cost = \
            SpatialEdge.compute_pylon_cost_and_tube_cost(elevation_profile)

    def to_abstract_edge(self):
        abstract_edge = abstract.AbstractEdge(self.start_spatial_point,
                                                self.end_spatial_point)
        return abstract_edge


class SpatialEdgesSets(abstract.AbstractEdgesSets):
    
    @staticmethod
    def is_spatial_edge_pair_compatible(spatial_edge_a, spatial_edge_b):
        edge_pair_compatible = \
            abstract.AbstractEdgesSets.is_edge_pair_compatible(spatial_edge_a,
                             spatial_edge_b, config.SPATIAL_DEGREE_CONSTRAINT)
        return edge_pair_compatible
    
    @staticmethod
    def test_path_points(path_points):
        sampled_path_points = interpolate.sample_path(path_points, 500)
        #print("sampled points: " + str(sampled_path_points))
                                               #config.BASE_RESOLUTION)
        x_spline, y_spline, s_values = interpolate.interpolate_points_2d(
                                                                sampled_path_points)
        curvature_array_2d = curvature.parametric_splines_2d_curvature(
                                                x_spline, y_spline, s_values)
        curvature_threshold = curvature.compute_curvature_threshold(
                                                parameters.MAX_SPEED/2.0,
                                                parameters.MAX_LATERAL_ACCEL)
        is_curvature_valid = curvature.test_curvature_validity(
                            curvature_array_2d, curvature_threshold)
        return is_curvature_valid
    
    @staticmethod
    def compute_spatial_degree_constraint(spatial_lattice): 
        spatial_degree_constraint = 90
        angle = math.radians(spatial_degree_constraint)
        length = spatial_lattice.spatial_x_spacing
        origin = [0, 0]
        pointA = [length, 0]
        pointB = util.round_nums([math.cos(angle) * length,
                                  math.sin(angle) * length])
        path_points = [pointA, origin, pointB]
        while not SpatialEdgesSets.test_path_points(path_points):
            print(spatial_degree_constraint)
            spatial_degree_constraint -= 1
            angle = math.radians(180 - spatial_degree_constraint)
            pointB = [math.cos(angle) * length, math.sin(angle) * length]
            path_points = [pointA, origin, pointB]
        return spatial_degree_constraint

    def __init__(self, spatial_lattice):
        spatial_degree_constraint = 25#self.compute_spatial_degree_constraint(
                                    #                           spatial_lattice)
        print("degree_constraint: " + str(spatial_degree_constraint))
        abstract.AbstractEdgesSets.__init__(self, spatial_lattice,
                                  SpatialEdge, spatial_degree_constraint)


def get_spatial_edges_sets(spatial_lattice):
    spatial_edges_sets = cacher.get_object("spatial_edges_sets",
        SpatialEdgesSets, [spatial_points_lattice], config.EDGES_FLAG)
    return spatial_edges_sets
