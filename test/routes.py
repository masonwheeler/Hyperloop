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
import parameters
import proj
import util
import visualize
import time


class Route:
    """For storing a single route option
    """

    def __init__(self, comfort, t, x, y, z, vx, vy, vz, ax, ay, az, land_cost,
                                                             land_elevations):

        self.latlngs = self.compute_latlngs(x, y)
        #self.land_cost = landcover.get_land_cost(self.latlngs)
        self.land_cost = land_cost
        self.tube_elevations = z
        self.pylons = self.compute_pylons(x, y, z, land_elevations)
        self.tube_cost = self.compute_tube_cost(x, y, z)
        self.pylon_cost = sum([pylon["pylonCost"] for pylon in self.pylons])
        self.velocity_profile = self.compute_velocity_profile(vx, vy, vz)
        self.acceleration_profile = self.compute_acceleration_profile(
            ax, ay, az)
        self.trip_time = t[-1]
        t_chunks = util.break_up(t, 500)
        t_comfort = [t_chunks[i][-1] for i in range(len(t_chunks))]
        self.comfort_rating = util.LpNorm(t_comfort, comfort, 10)

    def compute_latlngs(self, x, y):
        geospatials = np.transpose([x, y])
        return proj.geospatials_to_latlngs(geospatials, config.PROJ)

    def compute_pylons(self, x, y, z, land_elevations):
        geospatials = np.transpose([x, y])
        #s, zland = landscape.gen_landscape(geospatials, "elevation")

        def pylon_cost(pylon_height):
            if pylon_height > 0:
                return parameters.PYLON_BASE_COST + pylon_height * parameters.PYLON_COST_PER_METER
            else:
                return - pylon_height * parameters.TUNNELING_COST_PER_METER
        geospatials = [geospatial.tolist() for geospatial in geospatials]
        Pylons = [{"geospatial": geospatials[i],
                   "latlng": proj.geospatial_to_latlng(geospatials[i], config.PROJ),
                   "landElevation": land_elevations[i],
                   "pylonHeight": (z[i] - land_elevations[i]),
                   "pylonCost": pylon_cost(z[i] - land_elevations[i])}
                  for i in range(len(z))]
        return Pylons

    def compute_tube_cost(self, x, y, z):
        geospatials = np.transpose([x, y, z])
        tube_length = sum([np.linalg.norm(geospatials[i + 1] - geospatials[i])
                           for i in range(len(geospatials) - 1)])
        return tube_length * parameters.TUBE_COST_PER_METER

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
            "landCost": self.land_cost,
            "tubeCoords": self.tube_elevations.tolist(),
            "pylons": self.pylons,
            "tubeCost": self.tube_cost,
            "pylonCost": self.pylon_cost * 4,
            "totalCost": self.land_cost + self.tube_cost + self.pylon_cost,
            "velocityProfile": self.velocity_profile,
            "accelerationProfile": self.acceleration_profile,
            "comfortRating": self.comfort_rating,
            "tripTime": self.trip_time
            }
        return route_dict


# Ancillary Functions:

def graph_to_route_2d(graph, M):
    graph_geospatials = graph.geospatials
    route_2d = interp.para_super_q(graph_geospatials, M)
    return route_2d

def route_2d_to_route_3d(route_2d, elevation_tradeoff):
    arclengths, land_elevations = landscape.gen_landscape(route_2d,
                                                            "elevation")
    ##arclengths2 = [elevation_point["distance_along_path"] for elevation_point
    ##                                                    in elevation_profile]
    ##land_elevations2 = [elevation_point["land_elevation"] for elevation_point
    ##                                                    in elevation_profile]
    ##print(len(arclengths1))
    ##print(len(arclengths2))
    ##print(len(land_elevations1))
    ##print(len(land_elevations2))
    waypoint_arclengths, waypoint_tube_elevations = \
        landscape.match_landscape(arclengths, land_elevations,
                                  "elevation", elevation_tradeoff)
    tube_elevation_spline = PchipInterpolator(waypoint_arclengths,
                                              waypoint_tube_elevations)

    tube_elevations = tube_elevation_spline(arclengths)
    
    #start_arclength = arclengths[0]
    #end_arclength = arclengths[-1]
    #pylons_arclengths = np.arange(start_arclength, end_arclength,
    #                              parameters.PYLON_SPACING)
    #pylons_top_height_above_sealevel = tube_elevation_spline(pylons_arclengths)

    geospatials_x_vals, geospatials_y_vals = np.transpose(route_2d)
    route_3d = np.transpose([geospatials_x_vals,
                             geospatials_y_vals,
                             tube_elevations])
    return [route_3d, land_elevations]


def route_3d_to_route_4d(x, comfort_tradeoff1, comfort_tradeoff2):
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


def comfort_analysis_of_route_4d(x):
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
    ##print "computing data for a new route..."
    x = graph.geospatials
    graph_spacing = np.linalg.norm([x[2][0] - x[1][0], x[2][1] - x[1][1]])
    M = int(graph_spacing / (parameters.PYLON_SPACING * 4))
    ##print "interpolation sampling per edge is " + str(M)
    t_a = time.time()
    route_2d = graph_to_route_2d(graph, M)
    t_b = time.time()
    ##print "computed 2d route in: " + str(t_b - t_a) + " seconds."
    route_3d, land_elevations = route_2d_to_route_3d(route_2d, elevation_tradeoff)
    t_c = time.time()
    ##print "computed 3d route in: " + str(t_c - t_b) + " seconds."
    route_4d = route_3d_to_route_4d(route_3d, comfort_tradeoff1,
                                              comfort_tradeoff2)    
    t_d = time.time()
    ##print "computed 4d route in: " + str(t_d - t_c) + " seconds."
    comfort, t, x, y, z, vx, vy, vz, ax, ay, az = \
         comfort_analysis_of_route_4d(route_4d)
    t_e = time.time()
    ##print "completed comfort analysis in: " + str(t_e - t_d) + " seconds."
    route = Route(comfort, t, x, y, z, vx, vy, vz, ax, ay, az,
                             graph.land_cost, land_elevations)
    t_f = time.time()
    ##print "attached data to Route instance in: " + str(t_f - t_e) + " seconds."
    ##print "entire process took " + str(time.time() - start) + " seconds."
    return route

