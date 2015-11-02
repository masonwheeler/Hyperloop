"""
Original Developer: Jonathan Ward
Last Modified: 11/02/15
Last Modified By: Mason Wheeler
Last Modification Purpose: Adding alternate route functionality
"""

# Standard Modules:
import json

DROPBOX_DIRECTORY = "/home/ubuntu/Dropbox/htt_ro/RouteJson"

def save_routes_set(routes_set, index):
    """Saves completed routes to json
    """
    start_name = routes_set.spatial_metadata["startName"]
    end_name = routes_set.spatial_metadata["endName"]
    start_file_name = start_name.replace(" ", "_")
    end_file_name = end_name.replace(" ", "_")
    filename = "/" + start + "_to_" + end + "_routes(" + index + ").json"
    save_path = DROPBOX_DIRECTORY + filename
    print "Saving routes to: " + save_path
    with open(save_path, 'w') as file_path:
        json.dump(routes_set.as_dict(), file_path)
 
