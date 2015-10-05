"""
Original Developer: Jonathan Ward
"""

# Custom Modules:
import abstract_lattice
import config
import parameters
import util
import visualize


class TubePoint(abstract_lattice.AbstractPoint):

    def compute_pylon_cost(self):
        if self.is_undeground:
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

    def __init__(self, point_id, abstract_x_coord, abstract_y_coord, arc_length,
                       geospatial, latlng, tube_elevation, land_elevation):
        self.arc_length = arc_length
        self.latlng = latlng
        self.geospatial = geospatial
        self.land_elevation = land_elevation
        self.tube_elevtion = tube_elevation
        self.pylon_height = tube_elevation - land_elevation
        self.pylon_cost = self.compute_pylon_cost()
        self.physical_x_coord = distance_along_path
        self.physical_y_coord = tube_elevation
        abstract_lattice.AbstractPoint.__init__(self, point_id, abstract_x_coord,
                  abstract_y_coord, self.physical_x_coord, self.physical_y_coord)


class TubePointsSlice(abstract_lattice.AbstractSlice):

    @staticmethod
    def tube_points_slice_builder(abstract_x_coord, pylon_slice_bounds,
                                                  slice_start_point_id):
        tube_elevation_step_size = tube_points_slice_bounds["elevationStepSize"]
        min_tube_elevation = tube_points_slice_bounds["minTubeElevation"]
        max_tube_elevation = tube_points_slice_bounds["maxTubeElevation"]
        arc_length = tube_points_slice_bounds["arcLength"]
        geospatial = tube_points_slice_bounds["geospatial"]
        latlng = tube_points_slice_bounds["latlng"]
        land_elevation = tube_points_slice_bounds["landElevation"]

        tube_elevations = util.build_grid_1d(max_tube_elevation,
            min_tube_elevation, tube_elevation_step_size)
        point_id = slice_start_point_id
        abstract_y_coord = 0
        tube_points = []
        for tube_elevation in tube_elevations:
            tube_point = TubePoint(point_id,
                                   abstract_x_coord,
                                   abstract_y_coord,
                                   arc_length,
                                   geospatial
                                   latlng,
                                   tube_elevation,
                                   land_elevation)
            tube_points.append(tube_point)
            point_id += 1
            abstract_y_coord += 1
        return [tube_points, point_id]

    def __init__(self, abstract_x_coord, tube_points_slice_bounds,
                                             slice_start_point_id):
        abstract_lattice.AbstractSlice.__init__(self, abstract_x_coord,
                              tube_points_slice_bounds, slice_start_id,
                             TubePointsSlice.tube_points_slice_builder)


class TubePointsLattice(abstract_lattice.AbstractLattice):

    def __init__(self, elevation_profile):
        pylons_envelope_upper, pylons_envelope_lower = \
            self.build_pylons_envelopes(elevation_profile)
        pylons_slices_bounds = self.build_pylons_slices_bounds(
            elevation_profile, pylons_envelope_upper, pylons_envelope_lower)
        abstract_lattice.AbstractLattice.__init__(self, pylons_slices_bounds,
                                      PylonsSlice.pylon_slice_points_builder)

