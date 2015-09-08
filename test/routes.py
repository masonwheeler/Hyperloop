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

