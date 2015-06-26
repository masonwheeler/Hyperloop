"""
Runtime Parameters
"""
testingMode = True
verboseMode = False
timingMode = False
hasNlcd = False
cwd = ""

"""
Physical Constants.
"""
radiusOfEarth = 6.371*(10**6)

"""
Engineering constraints.
"""
pylonSpacing = 100.0 #maximum distance between subsequent pylons (in meters)
maxSpeed = 80 #maximum speed of the capsule (in m/s)

"""
Comfort constraints.
"""
gTolerance = 0.2 * 9.8

"""
For Runtime storage.
"""

cacheDirectory = ""
saveDirectory = ""
workingCacheName = ""
workingSaveDirName = ""
workingCacheDirectory = ""
workingSaveDirectory = ""


proj = 0
angle = 0
sizeFactor = 0
startVector = 0
directionsCoords = 0

"""
Polygon Generation Parameters.
"""

groupSize = 100 #The number of points in a polygon
polygonMergeChunkSize = 100 #the number of polygons to attempt to merge at once
tolerance = 10**-6 #the merge tolerance
maxAttempts = 10 #Maximum number of times to attempt to merge a polygon
Nth = 5 #Sample every Nth point in the polygon
finalBuffer = 10**-6 #The final buffer to apply to the polygon

"""
Lattice Generation Parameters.
"""

baseScale = 10**3 #distance between the start and end in lattice coordinates
latticeYSpacing = 1 #default spacing between lattice points vertically
latticeXSpacing = 10 #constant spacing between lattice points horizontally
degreeConstraint = 30 #the angular constraint between subsequent edges
numPaths = 1000 #the number of paths to output from the merge step
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

# Google Elevation API
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







