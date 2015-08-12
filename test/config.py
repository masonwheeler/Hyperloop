"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a namespace for global configuration variables.
Last Modified: 7/23/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Changed from routes to graphs
"""


########## Parameters And Switches ##########

"""
Modes and settings.
"""
testingMode = True
visualMode = False
verboseMode = False
timingMode = False
useDropbox = False

"""
Cache Overwriting Switches.
"""
useCachedDirections = False
useCachedSpline = True
useCachedLattice = True
useCachedEdges = True
useCachedGraphs = True

"""
Lattice Generation parameters
"""
pointSpacing = 2000 # (in meters) spacing between points in the same slice
directionsSampleSpacing = 10 # (in meters)
degreeConstraint = 30 #the angular constraint between subsequent edges
splineSampleSpacing = 1000 # (in units of directionsSampleSpacing) i.e.
                           # spacing between spline points in meters is given
                           # by directionsSampleSpacing * splineSampleSpacing
ndigits = 6 #the number of digits used for rounding

"""
Graph Generation parameters
"""
#numPaths = [300,250,200,150,100,50,25] # Number of paths to output from merging
#graphSampleSize = 10
graphCurvatureMinNumEdges = 3
graphSampleSpacing = 1000.0
numFronts = 12

"""
Engineering constraints.
"""
pylonSpacing = 100.0 #maximum distance between subsequent pylons (in meters)
maxSpeed = 330.0 #maximum speed of the capsule (in m/s)

"""
Pylon Cost parameters
"""
numHeights = 127

"""
Land Cost parameters
"""
landPointSpacing = 30.0 #spacing between points for land cost sampling in meters

"""
Comfort parameters.
"""
linearAccelTol = 0.5 * 9.81
lateralAccelTol = 0.3 * 9.81
jerkTol = 2
curvatureThreshhold = (lateralAccelTol / maxSpeed**2)

"""
Legal Parameters
"""

landPadding = 30

"""
Financial Parameters, all costs in dollars.
"""

rightOfWayLandCost = 0
pylonCostPerMeter = 10000
tunnelingCostPerMeter = 10000 # USD/m
pylonBaseCost = 2000
padding = 20   #padding (in meters)


#See (http://www.mrlc.gov/nlcd11_leg.php) for the pixel legend source.
#Note the omission of Alaska only values (please enter values in USD/ meter^2.)
costTable = {11: 300, #Open Water (Source: http://www.dot.state.fl.us/planning/policy/costs/Bridges.pdf)
             12: 4, #Perennial Ice/Snow
             21: 10,    #Developed, Open Space
             22: 20,    #Developed, Low Intensity
             23: 50,    #Developed, Medium Intensity
             24: 120,    #Developed, High Intensity
             31: 4,    #Barren Land
             41: 4,    #Deciduous Forest
             42: 4,    #Evergreen Forest
             43: 4,    #Mixed Forest
             52: 4,    #Shrub/Scrub
             71: 4,    #Grassland/Herbaceous
             81: 2,    #Pasture/Hay
             82: 2,    #Cultivated Crops
             90: 4,    #Woody Wetlands
             95: 4}   #Emergent Herbaceous Wetlands
                                     

########## For Internal Use ##########

"""
Overwriting Bools.
"""
directionsBools = [useCachedDirections]
splineBools = directionsBools + [useCachedSpline]
latticeBools = splineBools + [useCachedLattice]
edgesBools = latticeBools + [useCachedEdges]

graphsBools = edgesBools + [useCachedGraphs]

"""
Overwriting Flags.
"""
directionsFlag = all(directionsBools)
splineFlag = all(splineBools)
latticeFlag = all(latticeBools)
edgesFlag = all(edgesBools)
graphsFlag = all(graphsBools)

"""
Uninitialized Directory Paths.
"""
cacheDirectory = ""
saveDirectory = ""
workingCacheName = ""
workingSaveDirName = ""
workingCacheDirectory = ""
workingSaveDirectory = ""
workingGraphsDirectory = ""

"""
Unitialized Global variables.
"""

holder = 0
proj = 0
directionsCoords = 0
plotQueue = []


########## API-Specific and System-Specific Settings ##########

"""
For File Saving.
"""
cwd = ""
dropboxDirectory = "/home/ubuntu/Dropbox"

"""
For USGS-Elevation.
"""

usgsFtpPath = "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Elevation/13/IMG/"
usgsFolder = "/usgs/"

"""
For NLCD (National Landcover Dataset).
"""

geotiffFilePath = "/nlcd/us.tif"

"""
For Google-Elevation
"""

getElevationPieceSize = 512 #Constraint on number of simultaneous api calls.
elevationBaseUrl = 'https://maps.googleapis.com/maps/api/elevation/json'




