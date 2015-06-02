import config
import landCost
import pylonCost
import tubeCost

def get_latLngCost(latLng):
    landCost = landCost.get_latLngLandCost(latLng)
    tubeCost = 0
    pylonCost = 0
    return landCost + tubeCost + pylonCost
