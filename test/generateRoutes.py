import directionsCoords

def generateRoutes(origin,destination):
    coordinatesList = directionsCoords.get_coordinateList(origin,destination)
    print(coordinatesList)
    return 0
