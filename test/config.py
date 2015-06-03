"""
Physical Constants
"""

radiusOfEarth = 6.371*(10**6)

"""
Uninitialized, hence for storage.
"""

proj = 0
angle = 0
sizeFactor = 0
startVector = 0

"""
Initialized, for global usage.
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
rightOfWayDistance = 30

geotiffFilePath = ""

costTable = {}

"""
API-Specific, for robustness.
"""

getElevationPieceSize = 80
elevationBaseUrl = 'https://maps.googleapis.com/maps/api/elevation/json'















