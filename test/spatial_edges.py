"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To build edges with associated cost and elevation data
    from pairs of lattice points.

Last Modified:
    09/08/15

Last Modified By:
    Jonathan Ward

Last Modification Purpose:
    Moved degree constraint computations to independent module
"""

# Standard Modules:
import time
import numpy as np

# Custom Modules:
import abstract_edges
import angle_constraint
import cacher
import config
import curvature
import elevation
import landcover
import parameters
import util


class SpatialEdge(abstract_edges.AbstractEdge):

    ELEVATION_POINTS_TO_PYLON_POINTS_RATIO = 1

    def get_geospatials(self):
        self.geospatials = np.array([self.start_point.geospatial,
                                     self.end_point.geospatial])

    def get_latlngs(self, geospatials_to_latlngs):
        self.latlngs = geospatials_to_latlngs(self.geospatials)

    def compute_length(self):
        spatial_vector = util.edge_to_vector(self.geospatials)
        self.length = util.norm(spatial_vector)

    def get_coordinates(self, geospatials_to_latlngs):
        self.geospatials_to_latlngs = geospatials_to_latlngs
        self.get_geospatials()
        self.compute_length()
        self.get_latlngs(geospatials_to_latlngs)

    def compute_land_cost(self):
        if config.INCLUDE_LAND_COST:
            edge_is_in_right_of_way = (self.start_point.is_in_right_of_way and
                                       self.end_point.is_in_right_of_way)
            if edge_is_in_right_of_way:
                self.land_cost = landcover.RIGHT_OF_WAY_LAND_COST
            else:
                landcover_geospatials, distances = util.build_grid(
                                               self.start_point.geospatial,
                                               self.end_point.geospatial,
                                               landcover.LAND_POINT_SPACING)
                landcover_latlngs = self.geospatials_to_latlngs(
                                               landcover_geospatials)
                self.land_cost = landcover.get_land_cost(landcover_latlngs)
        else:
            self.land_cost = 0

    def get_elevation_profile(self):
        
        self.elevation_profile = \
            elevation.ElevationProfile.init_from_geospatial_pair(
              self.start_point.geospatial, self.end_point.geospatial,
              self.geospatials_to_latlngs,           
              self.ELEVATION_POINTS_TO_PYLON_POINTS_RATIO)
    
    def build_tube(self, tube_builder):
        #DEFAULT_MAX_CURVATURE = (parameters.MAX_VERTICAL_ACCEL /
        #                         parameters.MAX_SPEED**2)
        #max_curvature = DEFAULT_MAX_CURVATURE * 0.01
        #tube_profile = tube_builder(self.elevation_profile)#,
                                    #max_curvature=max_curvature)
        selected_tube_graphs = tube_builder(self.elevation_profile)
        tube_curvature_arrays = [graph.tube_curvature_array for graph in  
                                 selected_tube_graphs]
        test_graph = selected_tube_graphs[0]
        print test_graph.arc_lengths
        print tube_curvature_arrays[0]
        self.tube_curvature_array = tube_profile.tube_curvature_array
        self.pylon_cost = tube_profile.pylons_cost
        self.tube_cost = tube_profile.tube_cost 
        self.tunneling_cost = tube_profile.tunneling_cost
            
    def __init__(self, start_point, end_point):
        abstract_edges.AbstractEdge.__init__(self, start_point, end_point)

    def to_abstract_edge(self):
        abstract_edge = abstract_edges.AbstractEdge(self.start_point,
                                                      self.end_point)
        return abstract_edge

    def to_plottable_edge(self, color_string):
        geospatial_x_vals = [geospatial[0] for geospatial in self.geospatials]
        geospatial_y_vals = [geospatial[1] for geospatial in self.geospatials]
        plottable_points = [geospatial_x_vals, geospatial_y_vals]
        plottable_edge = [plottable_points, color_string]
        return plottable_edge


class SpatialEdgesSets(abstract_edges.AbstractEdgesSets):

    TUBE_READY = False

    NAME = "spatial_edges"
    FLAG = cacher.SPATIAL_EDGES_FLAG
    IS_SKIPPED = cacher.SKIP_EDGES

    def compute_spatial_degree_constraint(self, spatial_lattice):
        length_scale = spatial_lattice.parallel_resolution
        max_curvature = curvature.compute_curvature_threshold(
            parameters.MIN_SPEED, parameters.MAX_LATERAL_ACCEL)
        spatial_resolution = spatial_lattice.SPATIAL_BASE_RESOLUTION
        degree_constraint = angle_constraint.compute_angle_constraint(
                              length_scale, self.spatial_interpolator,
                                    max_curvature, spatial_resolution)
        return degree_constraint            

    def build_coordinates(self):
        for spatial_edges_set in self.filtered_edges_sets:
            for spatial_edge in spatial_edges_set:
                spatial_edge.get_coordinates(self.geospatials_to_latlngs)

    def build_elevation_profiles(self):
        for spatial_edges_set in self.filtered_edges_sets:
            for spatial_edge in spatial_edges_set:
                spatial_edge.get_elevation_profile()
    
    def compute_land_costs(self):
        for spatial_edges_set in self.filtered_edges_sets:
            for spatial_edge in spatial_edges_set:
                spatial_edge.compute_land_cost()

    def build_tubes(self):
        for spatial_edges_set in self.filtered_edges_sets:
            for spatial_edge in spatial_edges_set:
                spatial_edge.build_tube(self.tube_builder)

    def finish_edges_sets(self):
        util.smart_print("Now building elevation profiles")
        t1 = time.time()
        self.build_elevation_profiles()
        t2 = time.time()
        util.smart_print("Finished building elevation profiles in: " +
                         str(t2 - t1) + " seconds.")
        if self.TUBE_READY:
            util.smart_print("Now building tube profiles")
            self.build_tubes()
            t3 = time.time()
            util.smart_print("Finished building tube profiles in: " + str(t3 - t2)
                         + " seconds.")
        self.compute_land_costs()
   
    def __init__(self, spatial_lattice, spatial_interpolator,
                                                tube_builder):
        self.spatial_interpolator = spatial_interpolator
        self.tube_builder = tube_builder
        self.spatial_base_resolution = spatial_lattice.SPATIAL_BASE_RESOLUTION
        spatial_degree_constraint = self.compute_spatial_degree_constraint(
                                                           spatial_lattice)
        util.smart_print("The edge degree constraint is: " +
                         str(spatial_degree_constraint))
        self.spatial_metadata = spatial_lattice.spatial_metadata
        self.geospatials_to_latlngs = spatial_lattice.geospatials_to_latlngs
        abstract_edges.AbstractEdgesSets.__init__(self, spatial_lattice,
                                 SpatialEdge, spatial_degree_constraint)
        self.build_coordinates()
        self.finish_edges_sets()

    def get_plottable_edges(self, color_string):
        plottable_edges = []
        for edges_set in self.filtered_edges_sets:
            for edge in edges_set:
                plottable_edge = edge.to_plottable_edge(color_string)
                plottable_edges.append(plottable_edge)
        return plottable_edges

def get_spatial_edges_sets(*args):
    spatial_edges_sets = cacher.get_object(SpatialEdgesSets.NAME,
                                           SpatialEdgesSets,
                                           args,
                                           SpatialEdgesSets.FLAG,
                                           SpatialEdgesSets.IS_SKIPPED)
    return spatial_edges_sets
