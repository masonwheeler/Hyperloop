"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a namespace for global configuration variables.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Reorganization
"""


########## Parameters And Switches ##########

"""
Modes and settings.
"""
testingMode = True
visualMode = False
verboseMode = False
timingMode = False
hasNlcd = True
useDropbox = False

"""
Cache Overwriting Switches.
"""
useCachedDirections = False
useCachedSpline = True
useCachedLattice = True
useCachedEdges = True
useCachedRoutes = False

"""
Lattice Generation parameters
"""
pointSpacing = 2000 # (in meters) spacing between points in the same slice
directionsSampleSpacing = 10 # (in meters)
degreeConstraint = 30 #the angular constraint between subsequent edges
splineSampleSpacing = 1000 # (in units of directionsSampleSpacing) i.e.
                           # spacing between spline points in meters is given
                           # by directionsSampleSpacing * splineSampleSpacing
"""
Engineering constraints.
"""
pylonSpacing = 100.0 #maximum distance between subsequent pylons (in meters)
maxSpeed = 330 #maximum speed of the capsule (in m/s)
maxCost = 15000000000

"""
Pylon Cost parameters
"""
numHeights = 127

"""
Land Cost parameters
"""
landPointSpacing = 30 #spacing between points for land cost sampling in meters

"""
Comfort parameters.
"""
gTolerance = 0.5 * 9.8

"""
Legal Parameters
"""

landPadding = 30

"""
Financial Parameters, all costs in dollars.
"""

rightOfWayCost = 0
costPerPylonLength = 10000
pylonBaseCost = 2000
costTable = {}

########## For Internal Use ##########

"""
Overwriting Bools.
"""
directionsBools = [useCachedDirections]
splineBools = directionsBools + [useCachedSpline]
latticeBools = splineBools + [useCachedLattice]
edgesBools = latticeBools + [useCachedEdges]
routesBools = edgesBools + [useCachedRoutes]

"""
Overwriting Flags.
"""
directionsFlag = all(directionsBools)
splineFlag = all(splineBools)
latticeFlag = all(latticeBools)
edgesFlag = all(edgesBools)
routesFlag = all(routesBools)

"""
Uninitialized Directory Paths.
"""
cacheDirectory = ""
saveDirectory = ""
workingCacheName = ""
workingSaveDirName = ""
workingCacheDirectory = ""
workingSaveDirectory = ""

"""
Unitialized Global variables.
"""

proj = 0
directionsCoords = 0

"""
Lattice Generation Parameters.
"""

numPaths = 100 #the number of paths to output from the merge step
ndigits = 6 #the number of digits used for rounding

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




