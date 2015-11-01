"""
Original Developer: David Roberts
Purpose of Module: To generate a route from a graph.
Last Modified: 8/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add classes providing useful structure.
"""

# Custom Modules:
import util


class Route(object):    
    """For storing a single route option
    """
    def __init__(self, spatiotemporal_path_4d):
        self.accels_by_time = spatiotemporal_path_4d.accels_by_time.tolist()
        self.comfort_profile = spatiotemporal_path_4d.comfort_profile
        self.comfort_rating = spatiotemporal_path_4d.comfort_rating
        self.land_cost = spatiotemporal_path_4d.land_cost
        self.land_elevations = spatiotemporal_path_4d.land_elevations.tolist()
        self.latlngs = spatiotemporal_path_4d.latlngs.tolist()       
        self.pylons = spatiotemporal_path_4d.pylons
        self.pylon_count = len(self.pylons)
        self.pylon_cost = spatiotemporal_path_4d.pylon_cost
        self.speeds_by_time = spatiotemporal_path_4d.speeds_by_time.tolist()
        self.total_cost = round(spatiotemporal_path_4d.total_cost / 10.0**9, 3)
        self.total_distance = spatiotemporal_path_4d.total_distance
        self.trip_time = round(spatiotemporal_path_4d.trip_time / 60.0, 3)
        self.tube_cost = spatiotemporal_path_4d.tube_cost
        self.tube_elevations = spatiotemporal_path_4d.tube_elevations.tolist()
        self.tunneling_cost = spatiotemporal_path_4d.tunneling_cost

    def as_dict(self, index):
        route_dict = {
            "accelerationProfile": self.accels_by_time,
            "comfortProfile": self.comfort_profile,
            "comfortRating": self.comfort_rating,
            "index": index,
            "landCost": self.land_cost,
            "landElevations": self.land_elevations,
            "latlngs": self.latlngs,
            "pylons": self.pylons,
            "pylonCost": self.pylon_cost,
            "pylonCount" : self.pylon_count,
            "speedProfile": self.speeds_by_time,
            "totalCost": self.total_cost,
            "totalDistance" : self.total_distance,
            "tripTime": self.trip_time,
            "tubeCost": self.tube_cost,
            "tubeElevations": self.tube_elevations,
            "tunnelingCost": self.tunneling_cost
            }
        return route_dict


class RoutesSet(object):

    def build_routes_dicts_list(self, spatiotemporal_paths_sets_4d):
        routes = [Route(spatial_path_4d) for spatial_path_4d
                  in spatiotemporal_paths_sets_4d.selected_paths]
        routes_dicts_list = []
        for index in range(len(routes)):
            route_dict = routes[index].as_dict(index + 1)
            routes_dicts_list.append(route_dict)
        return routes_dicts_list    

    def get_plane_data(self):

    def get_train_data(self):

    def __init__(self, spatiotemporal_paths_sets_4d):
        self.spatial_metadata = spatiotemporal_paths_sets_4d.spatial_metadata
        plane_data = 
        self.routes_dicts_list = self.build_routes_dicts_list(
                            spatiotemporal_paths_sets_4d)       
 
    def as_dict(self):
        routes_set_dict = {
            "startCity": {
                "name": self.spatial_metadata["startName"],
                "coordinates": self.spatial_metadata["startLatLng"]
                },
            "endCity": {
                "name": self.spatial_metadata["endName"],
                "coordinates": self.spatial_metadata["endLatLng"]
                },
            "routes": self.routes_dicts_list
            }
        return routes_set_dict    
              

