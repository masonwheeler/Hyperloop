import config
import landcost
import pyloncost
import tubecost

def latlng_cost(latLng,primitiveVector):
    landCost = landcost.latlng_landcost(latLng)
    pylonCost = pylonCost.pylon_cost(latLng,primitiveVector,config.pylonSpacing,
            config.maxSpeed,config.gTolerance,config.costPerPylonLength,
            config.pylonBaseCost)    
    return landCost + pylonCost
