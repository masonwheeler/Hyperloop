"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a namespace for global configuration variables.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Moved unitialized directories.
"""



"""
Runtime Parameters.
"""
testingMode = True
visualMode = False
verboseMode = False
timingMode = False
hasNlcd = True
useDropbox = False
cwd = ""
dropboxDirectory = "/home/ubuntu/Dropbox"

"""
Cache Overwriting Switches.
"""

useCachedDirections = False
useCachedSpline = True
useCachedLattice = True
useCachedEdges = True
useCachedRoutes = False

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
New Lattice Generation parameters
"""

pointSpacing = 2000
directionsSampleSpacing = 10 # in meters
splineSampleSpacing = 1000 # spacing between spline points in meters is given by
                           #directionsSampleSpacing * splineSampleSpacing

degreeConstraint = 30 #the angular constraint between subsequent edges

"""
Engineering constraints.
"""
pylonSpacing = 100.0 #maximum distance between subsequent pylons (in meters)
maxSpeed = 330 #maximum speed of the capsule (in m/s)
maxCost = 15000000000
numHeights = 127

"""
Comfort constraints.
"""
gTolerance = 0.5 * 9.8

"""
For Runtime storage.
"""

proj = 0
directionsCoords = 0

"""
Lattice Generation Parameters.
"""

numPaths = 100 #the number of paths to output from the merge step
ndigits = 6 #the number of digits used for rounding

"""
For Usgs-Elevation.
"""

usgsFtpPath = "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Elevation/13/IMG/"
usgsFolder = "/usgs/"

"""
For Landcover.
"""

geotiffFilePath = "/nlcd/us.tif"
landPointSpacing = 30 #spacing between points for land cost sampling in meters

"""
For Google-Elevation
"""

getElevationPieceSize = 512 #Constraint on number of simultaneous api calls.
elevationBaseUrl = 'https://maps.googleapis.com/maps/api/elevation/json'

"""
Legal Parameters
"""

rightOfWayDistance = 30 #Distance right of way extends to on both sides of road.
landPadding = 30

"""
Financial Parameters, all costs in dollars.
"""

rightOfWayCost = 0
costPerPylonLength = 10000
pylonBaseCost = 2000

costTable = {}




