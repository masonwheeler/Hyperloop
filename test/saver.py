"""
Original Developer: Jonathan Ward
Last Modified: 11/02/15
Last Modified By: Mason Wheeler
Last Modification Purpose: Adding alternate route functionality
"""

DROPBOX_DIRECTORY = "/home/ubuntu/Dropbox/save"

import json

def save_routes_set(routes_set, index):
    """Saves completed routes to json
    """
    start = str(routes_set.start)
    end = str(routes_set.end)
    filename = "/" + start + "_to_" + end + "_routes(" + index + ").json"
    save_path = DROPBOX_DIRECTORY + filename
    print "Saving routes to: " + save_path
    with open(save_path, 'w') as file_path:
        #print json.dumps(routes_set.as_dict(), indent=4, separators=(',', ': '))
        json.dump(routes_set.as_dict(), file_path)

