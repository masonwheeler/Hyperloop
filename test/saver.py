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
    filename = "/" + start_name + "_to_" + end_name + "_routes.json"
    save_path = DROPBOX_DIRECTORY + filename
    print "Saving routes to: " + save_path
    with open(save_path, 'w') as file_path:
        #print json.dumps(routes_set.as_dict(), indent=4, separators=(',', ': '))
        json.dump(routes_set.as_dict(), file_path)
 
