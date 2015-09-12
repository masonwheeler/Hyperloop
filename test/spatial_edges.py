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

# Our Modules
import abstract_edges as abstract
import angle_constraint
import cacher
import config
import elevation
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
        self.latlngs = SpatialEdge.get_latlngs(start_spatial_point,
                                                 end_spatial_point)
        self.elevation_profile = SpatialEdge.get_elevation_profile(
                                                      self.geospatials)
        edge_is_in_right_of_way = (start_spatial_point.is_in_right_of_way and
                                     end_spatial_point.is_in_right_of_way)
        self.land_cost = SpatialEdge.compute_land_cost(edge_is_in_right_of_way,
                                                       self.geospatials)
        self.pylon_cost, self.tube_cost = \
            SpatialEdge.compute_pylon_cost_and_tube_cost(self.elevation_profile)

    def to_abstract_edge(self):
        abstract_edge = abstract.AbstractEdge(self.start_spatial_point,
                                                self.end_spatial_point)
        return abstract_edge


class SpatialEdgesSet(abstract.AbstractEdgesSet):
    
    def __init__(self, spatial_edges):
        set_geospatials_bounds = [spatial_edge.geospatials for spatial_edge
                                                    in spatial_edges]
        set_geospatial_partitions = [util.build_grid(geospatial_bound[0],
                                                     geospatial_bound[1],
                                                parameters.PYLON_SPACING)
                                     for geospatial_bound
                                     in set_geospatial_bounds]
        partitions_geospatials_grids = [geospatial_partition[0]
                                        for geospatial_partition
                                        in set_geospatial_partitions]
        partitions_latlngs_grids = [proj.geospatials_to_latlngs(
                                        geospatial_partition[0], config.PROJ)
                                    for geospatial_partition
                                    in set_geospatial_partitions]
        partitions_distances = [geospatial_partition[1]
                                for geospatial_partition
                                in set_geospatial_partitions]
        partitions_lengths = [len(partition_geospatial_grid)
                              for partition_geospatial_grid
                              in partitions_geospatials_grid]
        set_latlngs = util.fast_concat(partitions_latlngs_grids)
        set_elevations = elevation.usgs_windowed_elevation(set_latlngs)
        elevations_partitions = []
        last_index = 0
        for length in partitions_lengths:            
            elevations_partition = set_elevations[last_index:length]
            elevations_partitions.append(elevation_partition)
            last_index = length
        for i in range(len(elevation_partitions)):
            elevation_profile = elevation.build_elevation_profile(
                                              partitions_latlngs_grid[i],
                                              partitions_geospatials_grid[i],
                                              elevation_partitions[i],
                                              partitions_distances[i])
            spatial_edge = spatial_edges[i]
            spatial_edge.elevation_profile = elevation_profile
       
      


class SpatialEdgesSets(abstract.AbstractEdgesSets):
    
    def __init__(self, spatial_lattice, spatial_interpolator):
        spatial_degree_constraint = 25#self.compute_spatial_degree_constraint(
                                    #                           spatial_lattice)
        print("degree_constraint: " + str(spatial_degree_constraint))
        self.start = spatial_lattice.start
        self.end = spatial_lattice.end
        self.start_latlng = spatial_lattice.start_latlng
        self.end_latlng = spatial_lattice.end_latlng
        self.projection = spatial_lattice.projection
        abstract.AbstractEdgesSets.__init__(self, spatial_lattice,
            SpatialEdge, spatial_degree_constraint, spatial_interpolator)


def get_spatial_edges_sets(spatial_lattice, spatial_interpolator):
    spatial_edges_sets = cacher.get_object("spatial_edges_sets",
                                               SpatialEdgesSets,
                        [spatial_lattice, spatial_interpolator],
                                      config.SPATIAL_EDGES_FLAG)
    return spatial_edges_sets
