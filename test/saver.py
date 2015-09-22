"""
Original Developer: Jonathan Ward
"""

DROPBOX_DIRECTORY = "/home/ubuntu/Dropbox/save"


def save_routes_set(routes_set):
    """Saves completed routes to json
    """
    filename = "/" + str(routes_set.start) + "_" + str(routes_set.end) + ".json"
    save_path = DROPBOX_DIRECTORY + filename
    with open(save_path, 'w') as file_path:
        json.dump(routes_set.as_dict(), file_path)
 
