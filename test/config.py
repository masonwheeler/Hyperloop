"""
Physical Constants.
"""
radiusOfEarth = 6.371*(10**6)

"""
Engineering constraints.
"""
pylonSpacing = 100.0 #maximum distance between subsequent pylons (in meters)

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

"""
Initialized Algorithm paramters.
"""

groupSize = 100
polygonMergeChunkSize = 100
tolerance = 10**-6
maxAttempts = 10
baseScale = 10**3
sliceYSpacing = 1
latticeXSpacing = 10
ndigits = 6
Nth = 5
finalBuffer = 10**-6

"""
File paths.
"""

geotiffFilePath = "~/us.tif"


"""
API-Specific.
"""

# Google Elevation API
getElevationPieceSize = 80 #Constraint on number of simultaneous api calls.
elevationBaseUrl = 'https://maps.googleapis.com/maps/api/elevation/json'

"""
Legal Parameters
"""

rightOfWayDistance = 30 #Distance right of way extends to on both sides of road.

"""
Financial Parameters, all costs in dollars.
"""

costPerPylonLength = 10000
pylonBaseCost = 2000

costTable = {}







