"""
Original Developer: David Roberts
Purpose of Module: To generate a route from a graph.
Last Modified: 8/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add classes providing useful structure.
"""


class Route(object):    
    """For storing a single route option
    """
    def __init__(self, spatiotemporal_path_4d):
        self.scalar_acceleration_profile = \
            spatiotemporal_path_4d.scalar_acceleration_profile
        self.comfort_profile = spatiotemporal_path_4d.comfort_profile
        self.comfort_rating = spatiotemporal_path_4d.comfort_rating
        self.land_cost = spatiotemporal_path_4d.land_cost
        self.land_elevations = spatiotemporal_path_4d.land_elevations.tolist()
        self.latlngs = spatiotemporal_path_4d.latlngs.tolist()       
        self.pylons = spatiotemporal_path_4d.pylons
        self.pylon_cost = spatiotemporal_path_4d.pylon_cost
        self.speed_profile = spatiotemporal_path_4d.speed_profile
        self.total_cost = round(spatiotemporal_path_4d.total_cost / 10.0**9, 3)
        self.trip_time = round(spatiotemporal_path_4d.trip_time / 60.0, 3)
        self.tube_cost = spatiotemporal_path_4d.tube_cost
        self.tube_elevations = spatiotemporal_path_4d.tube_elevations.tolist()
        self.tunneling_cost = spatiotemporal_path_4d.tunneling_cost

    def as_dict(self, index):
        route_dict = {
            "accelerationProfile": self.scalar_acceleration_profile,
            "comfortProfile": self.comfort_profile,
            "comfortRating": self.comfort_rating,
            "index": index,
            "landCost": self.land_cost,
            "landElevations": self.land_elevations,
            "latlngs": self.latlngs,
            "pylons": self.pylons,
            "pylonCost": self.pylon_cost,
            "speedProfile": self.speed_profile,
            "totalCost": self.total_cost,
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

    def __init__(self, spatiotemporal_paths_sets_4d):
        self.spatial_metadata = spatiotemporal_paths_sets_4d.spatial_metadata
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
              

