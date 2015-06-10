import urllib
import simplejson

import config

def get_elevation(coords):
    args = {
        'locations': '|'.join([str(coord[0]) + ',' + str(coord[1]) for coord in coords])
    }

    url = config.elevationBaseUrl + '?' + urllib.urlencode(args)
    response = simplejson.load(urllib.urlopen(url))

    #Create a dictionary for each results[] object
    elevationArray = []

    for resultSet in response['results']:
        elevationArray.append(resultSet['elevation'])

    return elevationArray

