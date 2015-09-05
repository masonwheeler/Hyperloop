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

"""
class Edge:
    "
    Object that stores pairs of lattice points, the associated data

    Stores whether the line between the pair of points is in the right of way.
    Stores whether the edge is compatible with any other edges.
    "
    is_in_right_of_way = False
    is_useful = True
    land_cost = 0
    pylon_cost = 0
    angle = 0
    length = 0
    start_id = 0
    end_id = 0
    latlngs = []
    geospatials = []
    geospatial_vector = []

    def get_elevation_profile(self):
        start_geospatial, end_geospatial = self.geospatials
        pylon_slices_geospatials, pylon_slice_distances = util.build_grid(
            self.geospatial_vector, config.PYLON_SPACING, start_geospatial)
        self.elevation_profile = elevation.get_elevation_profile(
            pylon_slices_geospatials, pylon_slice_distances)

    def build_pylons(self):
        tube_cost, pylon_cost, tube_elevations = tube.build_tube_profile_v2(
            self.elevation_profile)
        # old_pylons = [{"geospatial" : elevation_point["geospatial"],
        #               "latlng" : elevation_point["latlng"],
        #               "elevation" : elevation_point["land_elevation"],
        #               "pylon_height" : 0,
        #               "pylon_cost" : 0}
        #               for elevation_point in self.elevation_profile]
        # pylons.build_pylons(old_pylons)
        # pylons.get_pyloncosts(old_pylons)
        #old_pylon_cost = pylons.edge_pyloncost(old_pylons)
        #print("old pylon cost: " + str(old_pylon_cost))
        self.pylon_cost = pylon_cost
        #print("pylon cost: " + str(pylon_cost))
        # if config.VISUAL_MODE:
        #    visualize.visualize_elevation_profile_v2(self.elevation_profile,
        #                                                    tube_elevations)

    def build_land_cost_samples(self):
        if self.is_in_right_of_way:
            self.land_cost = config.RIGHT_OF_WAY_LAND_COST
        else:
            start_geospatial, end_geospatial = self.geospatials
            landcover_geospatials, distances = util.build_grid(
                self.geospatial_vector, config.LAND_POINT_SPACING, start_geospatial)
            landcover_lat_lngs = proj.geospatials_to_latlngs(landcover_geospatials,
                                                             config.PROJ)
            landcover_cost_densities = landcover.landcover_cost_densities(
                landcover_lat_lngs)
            self.land_cost = landcover.cost_densities_to_landcost(
                landcover_cost_densities)

    def __init__(self, start_point, end_point):
        self.is_in_right_of_way = (start_point["is_in_right_of_way"]
                                   and end_point["is_in_right_of_way"])
        self.latlngs = [start_point["latlng_coords"],
                        end_point["latlng_coords"]]
        self.geospatials = [start_point["geospatial_coords"],
                            end_point["geospatial_coords"]]
        self.geospatial_vector = util.edge_to_vector(self.geospatials)
        start_geospatial, end_geospatial = self.geospatials
        start_x_val, start_y_val = start_geospatial
        end_x_val, end_y_val = end_geospatial
        self.start_id = start_point["point_id"]
        self.end_id = end_point["point_id"]
        self.angle = math.degrees(math.atan2(end_y_val - start_y_val,
                                             end_x_val - start_x_val))

    def as_dict(self):
        edge_dict = {"geospatials": self.geospatials,
                     "latlngs": self.latlngs,
                     "land_cost": self.land_cost,
                     "pylon_cost": self.pylon_cost}
        return edge_dict

    def display(self):
        print("The edge's cost is: " + str(self.cost) + ".")
        print("The edge's length is: " + str(self.length) + ".")
        print("The edge's lat-lng coords are: " + str(self.latlng_coords) + ".")
        print("The edge's xy coords are: " + str(self.geospatial_coords) + ".")
        print("The edge's angle is: " + str(self.angle) + " degrees.")


class EdgesSets:
    base_edges_sets = []
    filtered_edges_sets_list = []
    finished_edges_sets = []

    def base_edgessets(self, lattice):
        edges_sets = []
        for slice_index in range(len(lattice) - 1):
            slice_a = lattice[slice_index]
            slice_b = lattice[slice_index + 1]
            edges_set = []
            #print("points in slice")
            # for point in slice_a:
            #    print(str(point["geospatial_coords"]))
            # time.sleep(5)
            for start_point in slice_a:
                for end_point in slice_b:
                    new_edge = Edge(start_point, end_point)
                    # print(new_edge.geospatials)
                    # time.sleep(5)
                    edges_set.append(new_edge)
            edges_sets.append(edges_set)
        return edges_sets

    def edge_pair_compatible(self, edge_a, edge_b):
        if edge_a.end_id == edge_b.start_id:
            if abs(edge_a.angle - edge_b.angle) < config.DEGREE_CONSTRAINT:
                return True
        return False

    def determine_useful_edges(self, edges_sets):
        "An edge is useful if it has compatible edges in the adjacent \
         edge sets."

        "For edges in the first edge set."
        for edge_a in edges_sets[0]:
            "Check that each edge in the first edge set has an edge \
             which is compatible with it in the second edge set."
            compatibles = [self.edge_pair_compatible(edge_a, edge_b)
                           for edge_b in edges_sets[1]]
            edge_a.is_useful = any(compatibles)
        "For edges in the second through second to last edge set."
        for edge_set_index in range(1, len(edges_sets) - 1):
            for edge_b in edges_sets[edge_set_index]:
                "Check that each edge in the ith edge set has an edge \
                 which is compatible with it in the (i-1)th edge set \
                 and in the (i+1)th edge set."
                compatibles_a = [self.edge_pair_compatible(edge_a, edge_b)
                                 for edge_a in edges_sets[edge_set_index - 1]]
                compatibles_c = [self.edge_pair_compatible(edge_b, edge_c)
                                 for edge_c in edges_sets[edge_set_index + 1]]
                edge_b.is_useful = any(compatibles_a) and any(compatibles_c)
        "For edges in the last edge set."
        for edge_b in edges_sets[-1]:
            "Check that each edge in the last edge set has an edge which \
             is compatible with it in the second to last edge set."
            compatibles = [self.edge_pair_compatible(edge_a, edge_b)
                           for edge_a in edges_sets[-2]]
            edge_b.is_useful = any(compatibles)

    def filter_edges(self, edges_sets):
        filtered_edges_sets = []
        for edges_set in edges_sets:
            filtered_edges_set = filter(lambda edge: edge.is_useful, edges_set)
            filtered_edges_sets.append(filtered_edges_set)
        return filtered_edges_sets

    def check_empty(self, edges_sets):
        for edges_set in edges_sets:
            if len(edges_set) == 0:
                return True
        return False

    def iterative_filter(self):
        old_num_edges = util.list_of_lists_len(self.base_edges_sets)
        util.smart_print("The original number of spatial edges: " +
                         str(old_num_edges))

        filtered_edges_index = 0

        self.determine_useful_edges(self.base_edges_sets)
        filtered_edges = self.filter_edges(self.base_edges_sets)
        if self.check_empty(filtered_edges):
            raise ValueError("encountered empty edge")
        self.filtered_edges_sets_list.append(filtered_edges)
        flattened_filtered_edges = util.fast_concat(
            self.filtered_edges_sets_list[filtered_edges_index])
        new_num_edges = len(flattened_filtered_edges)

        while new_num_edges != old_num_edges:
            util.smart_print("The number of spatial edges is now: " +
                             str(new_num_edges))
            self.determine_useful_edges(
                self.filtered_edges_sets_list[filtered_edges_index])
            filtered_edges = self.filter_edges(
                self.filtered_edges_sets_list[filtered_edges_index])
            if self.check_empty(filtered_edges):
                raise ValueError("encountered empty edge")
            self.filtered_edges_sets_list.append(filtered_edges)
            filtered_edges_index += 1
            flattened_filtered_edges = util.fast_concat(
                self.filtered_edges_sets_list[filtered_edges_index])
            old_num_edges, new_num_edges = new_num_edges, len(
                flattened_filtered_edges)

    def build_land_cost_samples(self, edges_sets):
        for edges_set in edges_sets:
            for edge in edges_set:
                edge.build_land_cost_samples()

    def build_pylons(self, edges_sets):
        for edges_set in edges_sets:
            for edge in edges_set:
                edge.build_pylons()

    def get_elevation_profiles(self, edges_sets):
        for edges_set in edges_sets:
            for edge in edges_set:
                edge.get_elevation_profile()

    def __init__(self, lattice):
        self.base_edges_sets = self.base_edgessets(lattice)
        flattened_base_edges = util.fast_concat(self.base_edges_sets)
        self.iterative_filter()
        self.filtered_edges_sets = self.filtered_edges_sets_list[-1]
        t0 = time.time()
        self.get_elevation_profiles(self.filtered_edges_sets)
        t1 = time.time()
        util.smart_print("Retrieved elevation in " +
                         str(t1 - t0) + " seconds.")
        t0 = time.time()
        self.build_land_cost_samples(self.filtered_edges_sets)
        t1 = time.time()
        util.smart_print("Retrieved land cost in " +
                         str(t1 - t0) + " seconds.")
        self.build_pylons(self.filtered_edges_sets)


def build_pylons(edges_sets):
    for edges_set in edges_sets:
        for edge in edges_set:
            edge.build_pylons()


def build_edgessets(lattice):
    edges_sets = EdgesSets(lattice)
    finished_edges_sets = edges_sets.filtered_edges_sets
    return finished_edges_sets


def get_edgessets(lattice):
    finished_edges_sets = cacher.get_object("edgessets", build_edgessets,
                                            [lattice], config.EDGES_FLAG)
    return finished_edges_sets
"""

########## Spatial Edges ##########

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
        #print("curvature threshold: " + str(curvature_threshold))
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


#def build_spatial_edges_sets(spatial_lattice):
#    spatial_edges_sets = SpatialEdgesSets(spatial_points_lattice)
#    return spatial_edges_sets.final_edges_sets

def get_spatial_edges_sets(spatial_lattice):
    spatial_edges_sets = cacher.get_object("spatial_edges_sets",
        SpatialEdgesSets, [spatial_points_lattice], config.EDGES_FLAG)
    return spatial_edges_sets
