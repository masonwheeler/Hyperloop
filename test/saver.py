"""
Original Developer: Jonathan Ward
"""

DROPBOX_DIRECTORY = "/home/ubuntu/Dropbox/save"

import json

def save_routes_set(routes_set):
    """Saves completed routes to json
    """
    start_name = routes_set.spatial_metadata["startName"]
    end_name = routes_set.spatial_metadata["endName"]
    start_file_name = start_name.replace(" ", "_")
    end_file_name = end_name.replace(" ", "_")
    filename = "/" + start_file_name + "_to_" + end_file_name + "_routes.json"
    save_path = DROPBOX_DIRECTORY + filename
    print "Saving routes to: " + save_path
    with open(save_path, 'w') as file_path:
        json.dump(routes_set.as_dict(), file_path)
 
