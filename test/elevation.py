"""
Original Developer: Jonathan Ward
Purpose of Module: To obtain the elevation of each coordinate in
                   a list of latitude longitude coords.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify module usage.
"""

#Standard Modules
import urllib
import simplejson

#Our Modules
import config
import usgs
import proj

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

def usgs_elevation(latlngs):
    elevations = [usgs.get_elevation(latlng) for latlng in latlngs]
    return elevations

def get_elevation_profile(geospatials):
    latlngs = proj.geospatials_to_latlngs(geospatials, config.proj)
    elevations = usgs_elevation(latlngs)
    elevationProfile = [{"latlng" : latlngs[i],
                         "geospatial" : geospatials[i],
                         "landElevation" : elevations[i]}
                        for i in range(len(latlngs))]
    return elevationProfile
        
        

