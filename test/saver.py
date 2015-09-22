"""
Original Developer: Jonathan Ward
"""

DROPBOX_DIRECTORY = "/home/ubuntu/Dropbox/save"

import json

def save_routes_set(routes_set):
    """Saves completed routes to json
    """
    start = str(routes_set.start)
    end = str(routes_set.end)
    filename = "/" + start + "_to_" + end + "_routes.json"
    save_path = DROPBOX_DIRECTORY + filename
    with open(save_path, 'w') as file_path:
        json.dump(routes_set.as_dict(), file_path)
 
