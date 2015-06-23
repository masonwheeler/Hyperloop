"""
Runtime Parameters
"""
testingMode = True
hasNlcd = False
cwd = ""
usgsFolder = "/usgs/"

"""
Physical Constants.
"""
radiusOfEarth = 6.371*(10**6)

"""
Engineering constraints.
"""
pylonSpacing = 100.0 #maximum distance between subsequent pylons (in meters)
maxSpeed = 80 #maximum speed of the capsule (in ???)

"""
Comfort constraints.
"""
gTolerance = 0.2 * 9.8

"""
Uninitialized, hence for storage.
"""


proj = 0
angle = 0
sizeFactor = 0
startVector = 0
directionsCoords = 0

"""
Initialized Algorithm paramters.
"""

groupSize = 100
polygonMergeChunkSize = 100
tolerance = 10**-6
maxAttempts = 10
baseScale = 10**3 #distance between the start and end in lattice coordinates
latticeYSpacing = 1 #default spacing between lattice points vertically
latticeXSpacing = 10 #constant spacing between lattice points horizontally
degreeConstraint = 30
numPaths = 1000
ndigits = 6
Nth = 5
finalBuffer = 10**-6

"""
For Usgs-Elevation.
"""

usgsFtpPath = "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Elevation/13/IMG/"

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







