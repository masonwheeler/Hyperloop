"""
Original Developer: Jonathan Ward
Purpose of Module: To determine the tube/pylon cost component of an edge
Last Modified: 8/15/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To implement a non naive tube/pylon cost method.
"""
# Standard Modules
import numpy as np

# Our Modules
import abstract
import clothoid
import config
import interpolate
import mergetree
import velocity
import util

# Experimental Modules
from scipy.interpolate import PchipInterpolator
import routes
import match_landscape as landscape


class Pylon(abstract.AbstractPoint):

    def pylon_construction_cost(self, pylon_height):
        pylon_cost = config.PYLON_BASE_COST + \
            pylon_height * config.PYLON_COST_PER_METER
        return pylon_cost

    def __init__(self, pylon_id, lattice_x_coord, lattice_y_coord, distance_along_path,
                 geospatial, latlng, land_elevation, pylon_height):
        self.pylon_height = pylon_height
        self.land_elevation = land_elevation
        self.latlng = latlng
        tube_elevation = land_elevation + pylon_height
        x_value, y_value = geospatial
        z_value = tube_elevation
        self.tube_coords = [x_value, y_value, z_value]
        self.pylon_cost = self.pylon_construction_cost(pylon_height)
        self.spatial_x_coord = distance_along_path
        self.spatial_y_coord = tube_elevation
        abstract.AbstractPoint.__init__(self, pylon_id, lattice_x_coord,
                                        lattice_y_coord, self.spatial_x_coord, self.spatial_y_coord)


class PylonsSlice(abstract.AbstractSlice):

    @staticmethod
    def pylons_builder(lattice_x_coord, pylon_slice_bounds, shortest_pylon_id):
        pylon_height_step_size = pylon_slice_bounds["pylon_height_step_size"]
        tallest_pylon_height = pylon_slice_bounds["tallest_pylon_height"]
        shortest_pylon_height = pylon_slice_bounds["shortest_pylon_height"]
        pylon_height_difference = tallest_pylon_height - shortest_pylon_height
        distance_along_path = pylon_slice_bounds["distance_along_path"]
        geospatial = pylon_slice_bounds["geospatial"]
        latlng = pylon_slice_bounds["latlng"]
        land_elevation = pylon_slice_bounds["land_elevation"]
        shortest_pylon_height = 0
        pylon_height_options = util.build_grid_1d(pylon_height_difference,
                                                  pylon_height_step_size, shortest_pylon_height)
        pylon_ids = [index + shortest_pylon_id for index
                     in range(len(pylon_height_options))]
        pylons = []
        for i in range(len(pylon_ids)):
            pylon_id = pylon_ids[i]
            pylon_lattice_x_coord = lattice_x_coord
            pylon_lattice_y_coord = i
            pylon_distance_along_path = distance_along_path
            pylon_geospatial = geospatial
            pylon_lat_lng = latlng
            pylon_land_elevation = land_elevation
            pylon_height = pylon_height_options[i]
            new_pylon = Pylon(pylon_id, pylon_lattice_x_coord, pylon_lattice_y_coord,
                              pylon_distance_along_path, pylon_geospatial, pylon_lat_lng,
                              pylon_land_elevation, pylon_height)
            pylons.append(new_pylon)
        return pylons

    def __init__(self, lattice_x_coord, pylons_slice_bounds, shortest_pylon_id):
        abstract.AbstractSlice.__init__(self, lattice_x_coord, pylons_slice_bounds,
                                        shortest_pylon)


class PylonsLattice(abstract.AbstractLattice):

    def circle_function(self, x, r):
        if x > r:
            return -float("Inf")
        else:
            y = np.sqrt(np.square(r) - np.square(x)) - r
            return y

    def build_window(self, left_bound, right_bound, radius):
        relative_indices = range(-left_bound, right_bound + 1)
        window = [{"relative_index": relative_index,
                   "relative_elevation": self.circle_function(
                       abs(relative_index * config.PYLON_SPACING), radius)}
                  for relative_index in relative_indices]
        return window

    def add_current_window(self, envelope, current_window):
        for point in current_window:
            current_index = point["index"]
            envelope[current_index].append(point["elevation"])

    def build_envelope(self, elevations, radius):
        window_size = int(radius / config.PYLON_SPACING)
        envelope_lists = [[] for i in xrange(len(elevations))]
        for current_index in range(0, len(elevations)):
            if current_index < window_size:
                left_bound = current_index
            else:
                left_bound = window_size
            if current_index > (len(elevations) - 1) - window_size:
                right_bound = (len(elevations) - 1) - current_index
            else:
                right_bound = window_size
            relative_window = self.build_window(
                left_bound, right_bound, radius)
            current_elevation = elevations[current_index]
            current_window = [{
                "index": point["relative_index"] + current_index,
                "elevation": point["relative_elevation"] + current_elevation}
                for point in relative_window]
            self.add_current_window(envelope_lists, current_window)
        envelope = map(max, envelope_lists)
        return envelope

    def build_pylons_envelopes(self, elevation_profile):
        distances = []
        elevations = []
        for elevation_point in elevation_profile:
            distances.append(elevation_point["distance_along_path"])
            elevations.append(elevation_point["land_elevation"])
        upper_speed = config.MAX_SPEED
        curvature_threshold_upper = interpolate.compute_curvature_threshold(
            upper_speed, config.VERTICAL_ACCEL_CONSTRAINT)
        radius_upper = 1.0 / curvature_threshold_upper
        envelope_upper = self.build_envelope(elevations, radius_upper)
        lower_speed = config.MAX_SPEED / 1.2
        curvature_threshold_lower = interpolate.compute_curvature_threshold(
            lower_speed, config.VERTICAL_ACCEL_CONSTRAINT)
        radius_lower = 1.0 / curvature_threshold_lower
        envelope_lower = self.build_envelope(elevations, radius_lower)
        return [envelope_upper, envelope_lower]

    def envelope_point_to_bounds(self, data_point):
        elevation_point, envelope_point_upper, envelope_point_lower = data_point
        land_elevation = elevation_point["land_elevation"]
        pylons_slice_bounds = {
            "tallest_pylon_height": envelope_point_upper - land_elevation,
            "shortest_pylon_height": envelope_point_lower - land_elevation,
            "distance_along_path": elevation_point["distance_along_path"],
            "geospatial": elevation_point["geospatial"],
            "latlng": elevation_point["latlng"],
            "land_elevation": land_elevation,
            "pylon_height_step_size": config.PYLON_HEIGHT_STEP_SIZE
        }
        return pylons_slice_bounds

    def build_pylons_slices_bounds(self, elevation_profile, pylons_envelope_upper,
                                   pylons_envelope_lower):
        pylons_data = zip(elevation_profile, pylons_envelope_upper,
                          pylons_envelope_lower)
        pylons_slices_bounds = [self.envelope_point_to_bounds(data_point)
                                for data_point in pylons_data]
        return pylons_slices_bounds

    def __init__(self, elevation_profile):
        pylons_envelope_upper, pylons_envelope_lower = \
            self.build_pylons_envelopes(elevation_profile)
        pylons_slices_bounds = self.build_pylons_slices_bounds(elevation_profile,
                                                               pylons_envelope_upper, pylons_envelope_lower)
        abstract.AbstractLattice.__init__(self, pylons_slices_bounds,
                                          PylonsSlice.pylons_builder)


class TubeEdge(abstract.AbstractEdge):

    def tube_cost(self, start_pylon, end_pylon):
        start_tube_coords = start_pylon.tube_coords
        end_tube_coords = end_pylon.tube_coords
        tube_vector = util.edge_to_vector([start_tube_coords, end_tube_coords])
        tube_length = util.norm(tube_vector)
        tube_cost = tube_length * config.TUBE_COST_PER_METER
        return tube_cost

    def pylon_cost(self, start_pylon, end_pylon):
        total_pylon_cost = start_pylon.pylon_cost + end_pylon.pylon_cost
        return total_pylon_cost

    def __init__(self, start_pylon, end_pylon):
        abstract.AbstractEdge.__init__(self, start_pylon, end_pylon)
        self.tube_coords = [start_pylon.tube_coords, end_pylon.tube_coords]
        self.tube_cost = self.tube_cost(start_pylon, end_pylon)
        self.pylon_cost = self.pylon_cost(start_pylon, end_pylon)


class TubeEdgesSets(abstract.AbstractEdgesSets):

    def tube_edge_builder(self, start_pylon, end_pylon):
        tube_edge = TubeEdge(start_pylon, end_pylon)
        return tube_edge

    @staticmethod
    def is_tube_edge_pair_compatible(tube_edge_a, tube_edge_b):
        edge_pair_compatible = abstract.AbstractEdgesSets.is_edge_pair_compatible(
            tube_edge_a, tube_edge_b, config.TUBE_DEGREE_CONSTRAINT)
        return edge_pair_compatible

    def __init__(self, pylons_lattice):
        abstract.AbstractEdgesSets.__init__(self, pylons_lattice,
                                            self.tube_edge_builder, self.is_tube_edge_pair_compatible)


class TubeGraph(abstract.AbstractGraph):

    velocity_arc_length_step_size = config.VELOCITY_ARC_LENGTH_STEP_SIZE

    def compute_triptime_excess(self, tube_coords, num_edges):
        if num_edges < config.TUBE_TRIP_TIME_EXCESS_MIN_NUM_EDGES:
            return None
        else:
            z_values = [tube_coord[2] for tube_coord in tube_coords]
            local_max_allowed_vels = interpolate.points_1d_local_max_allowed_vels(
                z_values)
            triptime_excess = velocity.compute_local_trip_time_excess(
                local_max_allowed_vels, self.velocity_arc_length_step_size)
            return triptime_excess

    def __init__(self, start_id, end_id, start_angle, end_angle, num_edges,
                 tube_cost, pylon_cost, tube_coords):
        abstract.AbstractGraph.__init__(self, start_id, end_id,
                                        start_angle, end_angle, num_edges)
        self.tube_cost = tube_cost
        self.pylon_cost = pylon_cost
        self.tube_coords = tube_coords
        self.triptime_excess = self.compute_triptime_excess(
            tube_coords, num_edges)

    def tube_cost_trip_time_excess(self):
        cost_trip_time_excess = [self.tube_cost + self.pylon_cost,
                                 self.triptime_excess]
        #print("tube cost: " + str(self.tube_cost))
        #print("pylon cost: " + str(self.pylon_cost))
        #print("trip time excess: " + str(self.triptime_excess))
        return cost_trip_time_excess

    @classmethod
    def init_from_tube_edge(cls, tube_edge):
        start_id = tube_edge.start_id
        end_id = tube_edge.end_id
        start_angle = tube_edge.angle
        end_angle = tube_edge.angle
        num_edges = 1
        tube_cost = tube_edge.tube_cost
        pylon_cost = tube_edge.pylon_cost
        tube_coords = tube_edge.tube_coords
        data = cls(start_id, end_id, start_angle, end_angle, num_edges, tube_cost,
                   pylon_cost, tube_coords)
        return data

    @classmethod
    def merge_two_tube_graphs(cls, tube_graph_a, tube_graph_b):
        start_id = tube_graph_a.start_id
        end_id = tube_graph_b.end_id
        start_angle = tube_graph_a.start_angle
        end_angle = tube_graph_b.end_angle
        num_edges = tube_graph_a.num_edges + tube_graph_b.num_edges
        tube_cost = tube_graph_a.tube_cost + tube_graph_b.tube_cost
        pylon_cost = tube_graph_a.pylon_cost + tube_graph_b.pylon_cost
        tube_coords = util.smart_concat(tube_graph_a.tube_coords,
                                        tube_graph_b.tube_coords)
        data = cls(start_id, end_id, start_angle, end_angle, num_edges, tube_cost,
                   pylon_cost, tube_coords)
        return data


class TubeGraphsSet(abstract.AbstractGraphsSet):

    @staticmethod
    def is_graph_pair_compatible(graph_a, graph_b):
        graphs_compatible = abstract.AbstractGraphsSet.is_graph_pair_compatible(
            graph_a, graph_b, config.TUBE_DEGREE_CONSTRAINT)
        return graphs_compatible

    @staticmethod
    def tubegraphs_cost_triptime_excess(tube_graphs, graphs_num_edges):
        if graphs_num_edges < config.TUBE_TRIP_TIME_EXCESS_MIN_NUM_EDGES:
            return None
        else:
            graphs_cost_triptime_excess = [tube_graph.tube_cost_trip_time_excess()
                                           for tube_graph in tube_graphs]
            return graphs_cost_triptime_excess

    def __init__(self, tube_graphs, graphs_num_edges):
        minimize_cost = True
        minimize_triptime_excess = True
        abstract.AbstractGraphsSet.__init__(self, tube_graphs,
                                            self.tubegraphs_cost_triptime_excess, self.is_graph_pair_compatible,
                                            minimize_cost, minimize_triptime_excess, graphs_num_edges)

    @classmethod
    def init_from_tube_edges_set(cls, tube_edges_set):
        tube_graphs = map(TubeGraph.init_from_tube_edge, tube_edges_set)
        graphs_num_edges = 1
        return cls(tube_graphs, graphs_num_edges)


def tube_graphs_set_pair_merger(tube_graphs_set_a, tube_graphs_set_b):
    merged_tube_graphs = abstract.graphs_set_pair_merger(tube_graphs_set_a,
                                                         tube_graphs_set_b, TubeGraphsSet, TubeGraphsSet.is_graph_pair_compatible,
                                                         TubeGraph.merge_two_tube_graphs)
    return merged_tube_graphs


def build_tube_graphs(elevation_profile):
    pylons_lattice = PylonsLattice(elevation_profile)
    tube_edges_sets = TubeEdgesSets(pylons_lattice)
    tube_graphs_sets = map(TubeGraphsSet.init_from_tube_edges_set,
                           tube_edges_sets.final_edges_sets)
    tube_graphs_sets_tree = mergetree.MasterTree(tube_graphs_sets,
                                                 tube_graphs_set_pair_merger, abstract.graphs_set_updater)
    root_tube_graphs_set = tube_graphs_sets_tree.root
    selected_tube_graphs = root_tube_graphs_set.selected_graphs
    return selected_tube_graphs


def compute_pylon_cost(pylon_height):
    if pylon_height >= 0:
        height_cost = pylon_height * config.PYLON_COST_PER_METER
    else:
        height_cost = -pylon_height * 5 * config.PYLON_COST_PER_METER
    pylon_cost = config.PYLON_BASE_COST + height_cost
    return pylon_cost


def compute_tube_cost(tube_length):
    tube_cost = config.TUBE_COST_PER_METER * tube_length
    return tube_cost


def build_tube_profile_v2(elevation_profile):
    geospatials = [elevation_point["geospatial"] for elevation_point
                   in elevation_profile]
    land_elevations = [elevation_point["land_elevation"] for elevation_point
                       in elevation_profile]
    arc_lengths = [elevation_point["distance_along_path"] for elevation_point
                   in elevation_profile]
    s_interp, z_interp = landscape.match_landscape_v1(arc_lengths,
                                                      land_elevations, "elevation")
    tube_spline = PchipInterpolator(s_interp, z_interp)
    tube_elevations = tube_spline(arc_lengths)
    spatial_x_values, spatial_y_values = zip(*geospatials)
    pylon_heights = util.subtract(tube_elevations, land_elevations)
    tube_coords = zip(spatial_x_values, spatial_y_values, tube_elevations)
    tube_length = util.compute_total_arc_length(tube_coords)
    total_pylon_cost = sum(map(compute_pylon_cost, pylon_heights))
    total_tube_cost = compute_tube_cost(tube_length)
    return [total_tube_cost, total_pylon_cost, tube_elevations]

"""
def curvature(i, j, arc_lengths, elevations):
    x0, x1 = [arc_lengths[i], arc_lengths[j]]
    y0, y1 = [elevations[i], elevations[j]]
    tht0, tht1  = [0, 0]
    k, K, L = clothoid.build_clothoid(x0, y0, tht0, x1, y1, tht1)
    extremal_curvatures = [k + L*K, k]
    return max(np.absolute(extremal_curvatures))

def test(i, j, arc_lengths, elevations, cached):
    if cached[i][j]:
        return True
    else:
        cached[i][j] = cached[j][i] = True
        curvature_tol = config.linear_accel_constraint/config.MAX_SPEED**2
        return curvature(i, j, arc_lengths, elevations) > curvature_tol

def bad(index, tube_profile, arc_lengths, elevations, cached):       
    index_inserted_at = util.sorted_insert(index, tube_profile)
    backward_valid = test(tube_profile[index_inserted_at-1],
                          tube_profile[index_inserted_at],
                          arc_lengths, elevations, cached) 
    forward_valid = test(tube_profile[index_inserted_at],
                        tube_profile[index_inserted_at+1],
                        arc_lengths, elevations, cached)
    index_valid = backward_valid or forward_valid
    tube_profile.pop(index_inserted_at)
    return index_valid

def match_point(elevation_indices, tube_profile_indices,
                     arc_lengths, elevations, cached):
    i = 0
    while (bad(elevation_indices[i], tube_profile_indices,
                        arc_lengths, elevations, cached) and
                        i < len(elevation_indices) - 1):
        i += 1
    if i == len(elevation_indices) - 1:
        print "Exhausted the landscape. Could not find a point to match."
        return False
    else:
        util.sorted_insert(elevation_indices.pop(i), tube_profile_indices)
        return True

def reverse_sort_indices(a_list):
    list_indices = range(len(a_list))
    sorted_indices = sorted(list_indices, key = lambda i: a_list[i], reverse=True)
    return sorted_indices

def get_selected_tube_points(elevation_profile):
    #Add the endpoint indices to the tube profile
    tube_profile_indices = [0, len(elevation_profile)-1]
    elevations = [elevation_point["land_elevation"] for elevation_point
                                                 in elevation_profile]
    arc_lengths = [elevation_point["distance_along_path"] for elevation_point
                                                     in elevation_profile]
    #we now sort the remaining landscape.
    truncated_elevations = elevations[1 : len(elevations)]
    sorted_elevation_indices = reverse_sort_indices(truncated_elevations)
    elevation_indices = [index + 1 for index in sorted_elevation_indices]
    cached = [[0 for i in range(len(elevations))]
                 for i in range(len(elevations))]
    #l = 0
    while match_point(elevation_indices, tube_profile_indices,
                      arc_lengths, elevations, cached):
        pass
        #l += 1
        #print "matched the "+ str(l)+ "th point."
    selected_elevations = [elevations[index] for index in tube_profile]
    selected_arc_lengths = [arc_lengths[index] for index in tube_profile]
    return [selected_arc_lengths, selected_elevations]

def build_tube_profile(elevation_profile):    
    arc_lengths = [elevation_point["distance_along_path"] for elevation_point
                                                     in elevation_profile]
    selected_arc_lengths, selected_elevations = get_selected_tube_points(
                                                         elevation_profile)
    tube_spline = PchipInterpolator(selected_arc_lengths, selected_elevations)
    tube_elevations = tube_spline(arc_lengths)
    return tube_elevations
"""
