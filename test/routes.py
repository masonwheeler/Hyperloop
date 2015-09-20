"""
Original Developer: David Roberts
Purpose of Module: To generate a route from a graph.
Last Modified: 8/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add classes providing useful structure.
"""

# Standard Modules:
#import numpy as np

# Our Modules
#import cacher
#import config
#import elevation
#import landcover
#import parameters
#import proj
#import util
#import time

"""
class RouteV2:

    def __init__(self, comfort, t, x, y, z, vx, vy, vz, ax, ay, az, land_cost,
                                                             land_elevations):

        self.latlngs = self.compute_latlngs(x, y)
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
        return proj.geospatials_to_latlngs(geospatials, proj.PROJ)

    def compute_pylons(self, x, y, z, land_elevations):
        geospatials = np.transpose([x, y])

        def pylon_cost(pylon_height):
            if pylon_height > 0:
                return parameters.PYLON_BASE_COST + pylon_height * parameters.PYLON_COST_PER_METER
            else:
                return - pylon_height * parameters.TUNNELING_COST_PER_METER
        geospatials = [geospatial.tolist() for geospatial in geospatials]
        Pylons = [{"geospatial": geospatials[i],
                   "latlng": proj.geospatial_to_latlng(geospatials[i], proj.PROJ),
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
"""

class Route(object):    
    """For storing a single route option
    """
    def __init__(spatiotemporal_path_4d):
        self.acceleration_profile = spatiotemporal_path_4d.acceleration_profile
        self.comfort_rating = spatiotemporal_path_4d.comfort_rating
        self.comfort_profile = spatiotemporal_path_4d.comfort_profile
        self.land_cost = spatiotemporal_path_4d.land_cost
        self.land_elevations = spatiotemporal_path_4d.land_elevations
        self.latlngs = spatiotemporal_path_4d.latlngs
        self.pylons = spatiotemporal_path_4d.pylons
        self.pylon_cost = spatiotemporal_path_4d.pylon_cost
        self.total_cost = spatiotemporal_path_4d.total_cost
        self.trip_time = spatiotemporal_path_4d.trip_time
        self.tube_cost = spatiotemporal_path_4d.tube_cost
        self.tube_elevations = spatiotemporal_path_4d.tube_elevations
        self.velocityProfile = spatiotemporal_path_4d.velocity_profile

    def as_dict(self, index):
        route_dict = {
            "accelerationProfile": self.acceleration_profile,
            "comfortProfile": self.comfort_profile,
            "comfortRating": self.comfort_rating,
            "index": index,
            "landCost": self.land_cost,
            "landElevations": self.land_elevations,
            "latlngs": self.latlngs,
            "pylons": self.pylons,
            "pylonCost:" self.pylon_cost,
            "totalCost:" self.total_cost,
            "tripTime:" self.trip_time,
            "tubeCost:" self.tube_cost,
            "tubeElevations:" self.tube_elevations,
            "velocityProfile:" self.velocity_profile
            }
        return route_dict


class RoutesSet(object):

    def build_routes_dicts_list(self, spatiotemporal_paths_sets_4d):
        routes = [Route(spatial_path_4d) for spatial_path_4d
                  in spatiotemporal_paths_sets_4d.selected_paths]
        routes_dicts_list = []
        for index in range(len(routes)):
            routes_dicts_list.append(routes[i].as_dict, index + 1) 
        return routes_dicts_list

    def __init__(self, spatiotemporal_paths_sets_4d):
        self.start = spatiotemporal_paths_sets_4d.start
        self.end = spatiotemporal_paths_sets_4d.end
        self.start_latlng = spatiotemporal_paths_sets_4d.start_latlng
        self.end_latlng = spatiotemporal_paths_sets_4d.end_latlng
        self.routes_dicts_list = self.build_routes_dicts_list(
                            spatiotemporal_paths_sets_4d)
    
    def as_dict(self, routes_dicts_list):
        routes_set_dict = {
            "startCity": {
                "name": self.start,
                "coordinates": self.start_latlng
                },
            "endCity": {
                "name": self.end,
                "coordinates": end_lat_lng
                },
            "routes": self.routes_dicts_list
            }
        return routes_set_dict    
              

"""
def spatiotemporal_path_4d_to_route(spatiotemporal_path_4d):
    start = time.time()
    print "computing data for a new route..."
    t_c = time.time()
    tube_coords = spatiotemporal_path_4d.tube_coords
    land_elevations = spatiotemporal_path_4d.land_elevations
    land_cost = spatiotemporal_path_4d.land_cost
    t = spatiotemporal_path_4d.time_checkpoints
    x, y, z = zip(*spatiotemporal_path_4d.tube_coords)
    vx = spatiotemporal_path_4d.velocities_x_components
    vy = spatiotemporal_path_4d.velocities_y_components
    vz = spatiotemporal_path_4d.velocities_z_components
    ax = spatiotemporal_path_4d.accelerations_x_components
    ay = spatiotemporal_path_4d.accelerations_y_components
    az = spatiotemporal_path_4d.accelerations_z_components
    comfort_profile = spatiotemporal_path_4d.comfort_profile
    t_e = time.time()
    route = Route(comfort_profile, t, x, y, z, vx, vy, vz, ax, ay, az,
                                           land_cost, land_elevations)
    t_f = time.time()
    print "attached data to Route instance in: " + str(t_f - t_e) + " seconds."
    print "entire process took " + str(time.time() - start) + " seconds."
    return route
"""
