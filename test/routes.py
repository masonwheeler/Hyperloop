"""
Original Developer: David Roberts
Purpose of Module: To generate a route from a graph.
Last Modified: 8/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add classes providing useful structure.
"""

# Standard Modules:
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator

# Our Modules
import advanced_interpolate as interp
import cacher
import comfort as cmft
import config
import elevation
import landcover
import match_landscape as landscape
import proj
import util
import visualize
import time


# The Route Class.
class Route:

    def __init__(self, comfort, t, x, y, z, vx, vy, vz, ax, ay, az):

        self.latlngs = self.compute_latlngs(x, y)
        self.land_cost = landcover.get_land_cost(self.latlngs)
        self.tube_elevations = z
        self.pylons = self.compute_pylons(x, y, z)
        self.tube_cost = self.compute_tube_cost(x, y, z)
        self.pylon_cost = sum([pylon["pylon_cost"] for pylon in self.pylons])
        self.velocity_profile = self.compute_velocity_profile(vx, vy, vz)
        self.acceleration_profile = self.compute_acceleration_profile(
            ax, ay, az)
        self.trip_time = t[-1]
        print "trip_time is: " + str(self.trip_time)
        t_chunks = util.break_up(t, 500)
        t_comfort = [t_chunks[i][-1] for i in range(len(t_chunks))]
        self.comfort_rating = util.LpNorm(t_comfort, comfort, 10)
        print "comfort_rating is: " + str(self.comfort_rating)
        print "cost is: " + str((self.pylon_cost + self.tube_cost + self.land_cost) / 1000000000.0) + " billion USD."

    def compute_latlngs(self, x, y):
        geospatials = np.transpose([x, y])
        return proj.geospatials_to_latlngs(geospatials, config.PROJ)

    def compute_pylons(self, x, y, z):
        geospatials = np.transpose([x, y])
        s, zland = landscape.gen_landscape(geospatials, "elevation")

        def pylon_cost(pylon_height):
            if pylon_height > 0:
                return config.PYLON_BASE_COST + pylon_height * config.PYLON_COST_PER_METER
            else:
                return - pylon_height * config.TUNNELING_COST_PER_METER
        geospatials = [geospatial.tolist() for geospatial in geospatials]
        Pylons = [{"geospatial": geospatials[i],
                   "latlng": proj.geospatial_to_latlng(geospatials[i], config.PROJ),
                   "land_elevation": zland[i],
                   "pylon_height": (z[i] - zland[i]),
                   "pylon_cost": pylon_cost(z[i] - zland[i])}
                  for i in range(len(z))]
        return Pylons

    def compute_tube_cost(self, x, y, z):
        geospatials = np.transpose([x, y, z])
        tube_length = sum([np.linalg.norm(geospatials[i + 1] - geospatials[i])
                           for i in range(len(geospatials) - 1)])
        return tube_length * config.TUBE_COST_PER_METER

    def compute_velocity_profile(self, vx, vy, vz):
        velocity_vectors = np.transpose([vx, vy, vz])
        return [np.linalg.norm(velocity_vector) for velocity_vector in velocity_vectors]

    def compute_acceleration_profile(self, ax, ay, az):
        acceleration_vectors = np.transpose([ax, ay, az])
        return [np.linalg.norm(acceleration_vector) for acceleration_vector in acceleration_vectors]

    def as_dict(self, index):
        route_dict = {
            "index": index,
            "latlngs": self.latlngs,
            "land_cost": self.land_cost,
            "tube_coords": self.tube_elevations.tolist(),
            "pylons": self.pylons,
            "tube_cost": self.tube_cost,
            "pylon_cost": self.pylon_cost,
            "total_cost": self.land_cost + self.tube_cost + self.pylon_cost,
            "velocity_profile": self.velocity_profile,
            "acceleration_profile": self.acceleration_profile,
            "comfort_rating": self.comfort_rating,
            "trip_time": self.trip_time
        }
        return route_dict


# Ancillary Functions:

def graph_to_2_droute(graph, M):
    x = graph.geospatials
    return interp.para_super_q(x, M)


def graph_to_2_droutev2(graph, M):
    x = graph.geospatials
    return interp.scipy_q(x, M)


def _2_droute_to_3_droute(x, elevation_tradeoff):
    s, zland = landscape.gen_landscape(x, "elevation")
    s_interp, z_interp = landscape.match_landscape(
        s, zland, "elevation", elevation_tradeoff)
    f = PchipInterpolator(s_interp, z_interp)
    z = f(s)

    s_pylons = np.arange(s[0], s[-1], 100)
    z_pylons = f(s_pylons)

    x, y = np.transpose(x)
    return np.transpose([x, y, z])


def _3_droute_to_4_droute(x, comfort_tradeoff1, comfort_tradeoff2):
    s, vland = landscape.gen_landscape(x, "velocity")
    s_interp, v_interp = landscape.match_landscape(
        s, vland, "velocity", [comfort_tradeoff1, comfort_tradeoff2])
    f = PchipInterpolator(s_interp, v_interp)
    v = [max(10, f(s_val)) for s_val in s]

    t = [0] * len(v)
    t[1] = (s[1] - s[0]) / util.mean(v[0:2])
    for i in range(2, len(v)):
        t[i] = t[i - 1] + (s[i] - s[i - 1]) / v[i - 1]
    t[-1] = t[-2] + (s[-1] - s[-2]) / util.mean(v[-2:len(v)])

    x, y, z = np.transpose(x)
    return np.transpose([x, y, z, t])


def comfortanalysis__of_4_droute(x):
    x, y, z, t = np.transpose(x)
    vx, vy, vz, t = [util.numerical_derivative(x, t), util.numerical_derivative(
        y, t), util.numerical_derivative(z, t), t]
    ax, ay, az, t = [util.numerical_derivative(vx, t), util.numerical_derivative(
        vy, t), util.numerical_derivative(vz, t), t]

    # break_up data into chunks for comfort evaluation:
    v = np.transpose([vx, vy, vz])
    a = np.transpose([ax, ay, az])
    v_chunks = util.break_up(v, 500)
    a_chunks = util.break_up(a, 500)
    t_chunks = util.break_up(t, 500)

    mu = 1
    comfort = [cmft.sperling_comfort_index(v_chunks[i], a_chunks[i], t_chunks[
                                           i][-1] - t_chunks[i][0], mu) for i in range(len(t_chunks))]
    return [comfort, t, x, y, z, vx, vy, vz, ax, ay, az]


def graph_to_route(graph, elevation_tradeoff, comfort_tradeoff1, comfort_tradeoff2):
    start = time.time()
    print "computing data for a new route..."
    x = graph.geospatials
    graph_spacing = np.linalg.norm([x[2][0] - x[1][0], x[2][1] - x[1][1]])
    M = int(graph_spacing / config.PYLON_SPACING)
    print "interpolation sampling per edge is " + str(M)
    route_data = comfortanalysis__of_4_droute(_3_droute_to_4_droute(_2_droute_to_3_droute(
        graph_to_2_droute(graph, M), elevation_tradeoff), comfort_tradeoff1, comfort_tradeoff2))
    print "attaching data to new route..."
    print "done: process took " + str(time.time() - start) + " seconds."
    return Route(*route_data)


# class SpatialPath2d:
#     def sample_geospatials(self, graph_geospatials, geospatial_sample_distance):
#         sampled_geospatials = interpolate.sample_path(graph_geospatials,
#                                              geospatial_sample_distance)
#         return sampled_geospatials

#     def get_interpolating_geospatials(self, sampled_geospatials):
#         x_array, y_array = points_2d_to_arrays(sampled_geospatials)
#         num_points = len(sampled_geospatials)
#         s_values = interpolate.get_s_values(num_points)
#         x_spline, y_spline = interpolate.interpolating_splines_2d(x_array, y_array,
#                                                                        s_values)
#         x_values = interpolate.get_spline_values(x_spline, s_values)
#         y_values = interpolate.get_spline_values(y_spline, s_values)
#         interpolating_geospatials = [x_values, y_values]
#         return interpolating_geospatials

#     def get_interpolating_geospatials_v2(self, geospatials):
#         interpolating_geospatials_array = interp.para_super_q(geospatials, 25)
#         interpolating_geospatials = interpolating_geospatials_array.tolist()
#         arc_lengths = util.compute_arc_lengths(interpolating_geospatials)
#         return [interpolating_geospatials, arc_lengths]

#     def get_interpolating_latlngs(self, interpolating_geospatials):
#         interpolating_lat_lngs = proj.geospatials_to_latlngs(
#                          interpolating_geospatials, config.PROJ)
#         return interpolating_lat_lngs

#     #def get_tube_graphs(self, elevation_profile):

#     def get_tube_graphs_v2(self, elevation_profile):
#         geospatials = [elevation_point["geospatial"] for elevation_point
#                                                     in elevation_profile]
#         land_elevations = [elevation_point["land_elevation"] for elevation_point
#                                                          in elevation_profile]
#         arc_lengths = [elevation_point["distance_along_path"] for elevation_point
#                                                          in elevation_profile]
#         s_interp, z_interp = landscape.match_landscape(arc_lengths,
#                                    land_elevations, "elevation")
#         tube_spline = PchipInterpolator(s_interp, z_interp)
#         tube_elevations = tube_spline(arc_lengths)
#         #  plt.plot(arc_lengths, tube_elevations, 'b.',
#         #            arc_lengths, land_elevations, 'r.')
#         #  plt.show()
#         spatial_x_values, spatial_y_values = zip(*geospatials)
#         tube_graph = zip(spatial_x_values, spatial_y_values, tube_elevations)
#         tube_graphs = [tube_graph]
#         return tube_graphs

#     def __init__(self, spatial_graph):
#         graph_geospatials = spatial_graph.geospatials
#         #sampled_geospatials = self.sample_geospatials(graph_geospatials)
#         #interpolating_geospatials = self.get_interpolating_geospatials(
#         #                                               sampled_geospatials)
#         interpolating_geospatials, arc_lengths = \
#           self.get_interpolating_geospatials_v2(graph_geospatials)
#         interpolating_lat_lngs = self.get_interpolating_latlngs(
#                                            interpolating_geospatials)
#         self.elevation_profile = elevation.get_elevation_profile(
#                             interpolating_geospatials, arc_lengths)
#         self.land_cost = landcover.get_land_cost(interpolating_lat_lngs)
#         #self.tube_graphs = self.get_tube_graphs_v2(self.elevation_profile)

# def build_spatial_paths_2d(complete_spatial_graphs):
#     spatial_paths2d = map(SpatialPath2d, complete_spatial_graphs)
#     return spatial_paths2d

# def get_spatial_paths_2d(complete_spatial_graphs):
#     spatial_paths2d = cacher.get_object("spatialpaths2d", build_spatial_paths_2d,
#                           [complete_spatial_graphs], cacher.save_spatial_paths_2d,
#                                                       config.SPATIAL_PATHS2d_flag)
#     return spatial_paths2d
