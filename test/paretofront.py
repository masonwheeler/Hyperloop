"""
Original Developer: Jonathan Ward
Purpose of Modules: To compute the 2d Pareto Front.
Last Modified: 7/28/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add comments.
"""

import scipy
import numpy as np

class ParetoFront:
    """
    Computes nested Pareto Frontiers of points in 2d.

    Calculates the Convex Hull of the set of points using qhull,
    then computes the Pareto Front of those points.
    """
    pointsArray = [] #Numpy array containing original points.
    prunedPointsIndices = [] #Contains the indices of the pruned points.
    frontsIndices = [] #Contains the indices of the points in each fronts.
    xReverse = False #If set to true, the front minimizes x-values.
    yReverse = False #If set to true, the front minimizes y-values.

    def vertices_to_frontindices(self, vertices, xReverse, yReverse):
        """
        Computes the Pareto front given the vertices of the convex hull.

        If xReverse is set to True then the Pareto front minimizes x-values.
        If yReverse is set to True then the Pareto front minimizes y-values.
        """
        xMax, yMax = np.amax(vertices, axis = 0)
        ##print("x Max: " + str(xMax))        
        ##print("y Max: " + str(yMax))
        xMin, yMin = np.amin(vertices, axis = 0)
        ##print("x Min: " + str(xMin))        
        ##print("y Min: " + str(yMin))
        #The vertices with x-values equal to x-max
        xMaxVertices = vertices[np.where(vertices[:,0] == xMax)]   
        ##print("x max vertices: " + str(xMaxVertices))
        #The vertices with y-values equal to y-max
        yMaxVertices = vertices[np.where(vertices[:,1] == yMax)]           
        #The vertices with x-values equal to x-min
        xMinVertices = vertices[np.where(vertices[:,0] == xMin)]
        ##print("x min vertices: " + str(xMinVertices))
        #The vertices with y-values equal to y-min
        yMinVertices = vertices[np.where(vertices[:,1] == yMin)]           
        ##print("y min vertices: " + str(yMinVertices))
         
        if (not xReverse and not yReverse): #Taking the top-right vertices
            #To find the maximum y-value of the vertices with maximal x-values
            xMax, xMaxVerticesYMax = np.amax(xMaxVertices, axis=0)
            #To find the maximum x-value of the vertices with maximal y-values
            yMaxVerticesXMax, yMax = np.amax(yMaxVertices, axis=0)
            #Set the minimum acceptable x-value for the x-value filter
            xMinFilter = yMaxVerticesXMax
            #Set the minimum acceptable y-value for the y-value filter
            yMinFilter = xMaxVerticesYMax
            #Take the vertices which pass the x-value and y-value filters.
            frontIndices = np.where(np.logical_and(
                             vertices[:,0] >= xMinFilter,
                             vertices[:,1] >= yMinFilter))
            return frontIndices                    
         
        if (not xReverse and yReverse): #Taking the bottom-right vertices
            #To find the minimum y-value of the vertices with maximal x-values
            xMax, xMaxVerticesYMin = np.amin(xMaxVertices, axis=0)
            #To find the maximum x-value of the vertices with minimal y-values
            yMinVerticesXMax, yMin = np.amax(yMinVertices, axis=0)
            #Set the minimum acceptable x-value for the x-value filter
            xMinFilter = yMinVerticesXMax
            #Set the maximum acceptable y-value for the y-value filter
            yMaxFilter = xMaxVerticesYMin
            #Take the vertices which pass the x-value and y-value filters.
            frontIndices = np.where(np.logical_and(
                             vertices[:,0] >= xMinFilter,
                             vertices[:,1] <= yMaxFilter))
            return frontIndices                   
        
        if (xReverse and not yReverse): #Taking the top-left vertices
            #To find the maximum y-value of the vertices with minimal x-values
            xMin, xMinVerticesYMax = np.amax(xMinVertices, axis=0)
            #To find the minimum x-value of the vertices with maximal y-values
            yMaxVerticesXMin, yMax = np.amin(yMaxVertices, axis=0)
            #Set the maximum acceptable x-value for the x-value filter
            xMaxFilter = yMaxVerticesXMin
            #Set the minimum acceptable y-value for the y-value filter
            yMinFilter = xMinVerticesYMax
            #Take the vertices which pass the x-value and y-value filters.
            frontIndices = np.where(np.logical_and(
                             vertices[:,0] <= xMaxFilter,
                             vertices[:,1] >= yMinFilter))
            return frontIndices                    
         
        if (xReverse and yReverse): #Taking the bottom-left vertices
            ##print("minimizing x and y")
            #To find the minimum y-value of the vertices with minimal x-values
            xMin, xMinVerticesYMin = np.amin(xMinVertices, axis=0)
            #To find the minimum x-value of the vertices with minimal y-values
            yMinVerticesXMin, yMin = np.amin(yMinVertices, axis=0)
            #Set the maximum acceptable x-value for x-value filter
            xMaxFilter = yMinVerticesXMin
            ##print("x max filter: " + str(xMaxFilter))
            #Set the maximum acceptable y-value for y-value filter
            yMaxFilter = xMinVerticesYMin            
            ##print("y max filter: " + str(yMaxFilter))
            #Take the vertices which pass the x-value and y-value filters.
            frontIndices = np.where(np.logical_and(
                             vertices[:,0] <= xMaxFilter,
                             vertices[:,1] <= yMaxFilter))
            selectedVertices = vertices[frontIndices]
            print("selected vertices: ")
            print(str(selectedVertices))
            return frontIndices      

    def remove_frontindices(self, frontIndicesRelPoints):
        """Gives the indices of the points without the indices of the front."""
        self.prunedPointsIndices = np.setdiff1d(self.prunedPointsIndices,
                                                frontIndicesRelPoints)
 
    def remove_duplicates(self, pointsArray):
        """Gives the indices of the unique points."""
        #reshapes the points array into an array of tuples
        #print("original points: " + str(pointsArray))
        tuplesArray = np.ascontiguousarray(pointsArray).view(
        np.dtype((np.void, pointsArray.dtype.itemsize * pointsArray.shape[1])))        
        #selects the indices of the unique tuples.
        _, uniqueIndices = np.unique(tuplesArray, return_index=True)
        #print("total number of points: " + str(pointsArray.shape[0]))
        #print("number of unique points: " + str(uniqueIndices.size))
        ##print("unique indices: ")
        ##print(str(uniqueIndices))
        sortedUniqueIndices = sorted(uniqueIndices)
        ##print("sorted indices")
        ##print(str(sortedUniqueIndices))
        return sortedUniqueIndices

    def __init__(self, points, xReverse, yReverse):
        self.frontsIndices = []
        ##print("created new pareto front with points: ")
        ##print(points)
        self.xReverse, self.yReverse = xReverse, yReverse
        #Raw points array may contain duplicates
        rawPointsArray = np.array(map(np.array, points))
        #The indices of the unique points in the raw points array.        
        uniqueIndices = self.remove_duplicates(rawPointsArray)
        #The unique points in the raw points array.
        self.pointsArray = rawPointsArray[uniqueIndices]
        #The number of rows in the points array
        numPoints = self.pointsArray.shape[0]
        #set the indices of the pruned points as the indices of all points
        self.prunedPointsIndices = np.arange(numPoints)
        #At least 3 points are needed to build a convex hull
        if numPoints < 3:                     
            #if there are no points, raise a value error.
            if numPoints == 0:
                print("No points passed to Pareto Front")
                raise ValueError("No Points passed to Pareto Front")
            else:   
                #if there are 1 or 2 points, add these to the fronts
                #print("added last points")
                frontIndices = self.prunedPointsIndices
                self.frontsIndices.append(frontIndices.tolist())
                self.remove_frontindices(frontIndices)
        else:
            #If there are enough points, try to build a convex hull.
            try:
                convexHull = scipy.spatial.ConvexHull(self.pointsArray)
            #If convex hull not built, raise a value error.
            except scipy.spatial.qhull.QhullError:
                print("all points are in a line.")
                raise ValueError("All points are in a line.")
            #If another strange error occurs, record that.
            except ValueError:
                print("Qhull encountered other error")
                raise ValueError("Qhull encountered other error")
            #The indices of the vertices in the convex hull in the points array
            hullIndices = convexHull.vertices
            #The vertices in the convex hull.
            hullVertices = self.pointsArray[hullIndices]
            #The indices of the points in the pareto front in the hull array.
            frontIndicesRelHull = self.vertices_to_frontindices(hullVertices,
                                                self.xReverse, self.yReverse)
            #The indices of the points in the pareto front in the points array.
            frontIndicesRelPoints = hullIndices[frontIndicesRelHull]
            selectedPoints = self.pointsArray[frontIndicesRelPoints]
            #print("selected points: ")
            #print(str(selectedPoints))
            #print("selected points indices: ")
            ##print(str(frontIndicesRelPoints))
            #Add the indices of the points in the pareto front to list.
            self.frontsIndices.append(frontIndicesRelPoints.tolist())
            #Remove the indices of the points in the pareto front from list.
            self.remove_frontindices(frontIndicesRelPoints)
        print("the selected points are: ")
        selectedPoints = [points[i] for i in self.frontsIndices[-1]]
        print(selectedPoints)

    def build_nextfront(self):
        """
        Build the Pareto front of the points with the last front removed

        If the next front is successfully built return True, otherwise False.
        Since points array does not have duplicates,
        the pruned points array does not have duplicates.
        """
        ##print("build next front")
        #Initialize the points which have not been in a front yet
        prunedPoints = self.pointsArray[self.prunedPointsIndices]
        #The number of rows in the pruned points array
        numPointsLeft = prunedPoints.shape[0]
        #At least 3 points are needed to build a convex hull
        if numPointsLeft < 3:
            #If there are no points, record failure
            if numPointsLeft == 0:
                return False
            else:
                #If there are 1 or 2 points, add them to the front
                frontIndicesRelPoints = self.prunedPointsIndices
                self.frontsIndices.append(frontIndicesRelPoints.tolist())
                self.remove_frontindices(frontIndicesRelPoints)
                return True
        else:
            #If there are enough points, try to build a convex hull
            try:               
                convexHull = scipy.spatial.ConvexHull(prunedPoints)
            #if convex hull not built, raise a value error.
            except scipy.spatial.qhull.QhullError:
                print("all points are in a line.")
                raise ValueError("All points are in a line.")
            #If another strange error occurs, record that.
            except ValueError:
                print("Qhull encountered other error")
                raise ValueError("Qhull encountered other error")
            #The indices of the vertices in the convex hull 
            # relative to the pruned points array
            hullIndicesRelPrunedPoints = convexHull.vertices
            #The indices of the vertices in the convex hull
            # relative to the points array
            hullIndicesRelPoints = self.prunedPointsIndices[
                                            hullIndicesRelPrunedPoints]
            #The vertices in the convex hull
            hullVertices = self.pointsArray[hullIndicesRelPoints]
            #The indices of the points in the front 
            # relative to the convex hull.
            frontIndicesRelHull = self.vertices_to_frontindices(hullVertices,
                                                self.xReverse, self.yReverse)
            #The indices of the points in the front
            # relative to the points array.
            frontIndicesRelPoints = hullIndicesRelPoints[frontIndicesRelHull]
            #Add the indices of the points in the pareto front to list.
            ##print("front indices: " + str(frontIndicesRelPoints))          
            frontIndicesList = frontIndicesRelPoints.tolist()
            ##print(frontIndicesList)
            self.frontsIndices.append(frontIndicesList)          
            #Remove the indices of the points in the pareto front from list.
            self.remove_frontindices(frontIndicesRelPoints)            
            return True          

