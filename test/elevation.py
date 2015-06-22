import urllib
import simplejson

import config
import usgs

def google_elevation(coords):
    args = {
        'locations': '|'.join([str(coord[0]) + ',' + str(coord[1]) for coord in coords])
    }

    url = config.elevationBaseUrl + '?' + urllib.urlencode(args)
    response = simplejson.load(urllib.urlopen(url))

    elevationArray = []
    if response['status'] == 'OK':	 
        #Create a dictionary for each results[] object
        for resultSet in response['results']:
            elevationArray.append(resultSet['elevation'])
    else:
        print(response['status'])

    return elevationArray

def usgs_elevation(coords):
    elevations = [usgs.get_elevation(latlngCoord) for latlngCoord in coords]
    return elevations


coords = [(37.7833,-122.4167), (34.0500, -118.2500)]

googleElevation = google_elevation(coords)
usgsElevation = usgs_elevation(coords)
print("Google gives " + str(googleElevation))
print("USGS gives " + str(usgsElevation))
