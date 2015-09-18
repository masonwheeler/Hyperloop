"""
Original Developer: Jonathan Ward
"""

DROPBOX_DIRECTORY = "/home/ubuntu/Dropbox/save"

def save_routes(routes, start, end, start_lat_lng, end_lat_lng):
    """Saves completed routes to json
    """
    routes_dicts = []
    route_index = 0
    for route in routes:
        route_dict = route.as_dict(route_index)
        route_index += 1
        routes_dicts.append(route_dict)
    city_pair = {
        "startCity": {
            "name": start,
            "coordinates": start_lat_lng
        },
        "endCity": {
            "name": end,
            "coordinates": end_lat_lng
        },
        "routes": routes_dicts
    }
    filename = "/" + str(start) + "_" + str(end) + ".json"
    save_path = DROPBOX_DIRECTORY + filename
    with open(save_path, 'w') as file_path:
        json.dump(city_pair, file_path)

