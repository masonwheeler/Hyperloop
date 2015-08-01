"""
Original Developer: Jonathan Ward
Purpose of Modules: To compute the 2d Pareto Front.
Last Modified: 7/28/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add comments.
"""

import scipy.spatial
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
        xMin, yMin = np.amin(vertices, axis = 0)
         
        if (not xReverse and not yReverse): #Taking the top-right vertices
            #The vertices with x-values equal to x-max
            xMaxVertices = vertices[np.where(vertices[:,0] == xMax)]
            #The vertices with y-values equal to y-max
            yMaxVertices = vertices[np.where(vertices[:,1] == yMax)]           
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
            #The vertices with x-values equal to x-max
            xMaxVertices = vertices[np.where(vertices[:,0] == xMax)]
            #The vertices with y-values equal to y-min
            yMinVertices = vertices[np.where(vertices[:,1] == yMin)]           
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
            #The vertices with x-values equal to x-min
            xMinVertices = vertices[np.where(vertices[:,0] == xMin)]
            #The vertices with y-values equal to y-max
            yMaxVertices = vertices[np.where(vertices[:,1] == yMax)]           
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
            #The vertices with x-values equal to x-min
            xMinVertices = vertices[np.where(vertices[:,0] == xMin)]
            #The vertices with y-values equal to y-min
            yMinVertices = vertices[np.where(vertices[:,1] == yMin)]           
            #To find the minimum y-value of the vertices with minimal x-values
            xMin, xMinVerticesYMin = np.amin(xMinVertices, axis=0)
            #To find the minimum x-value of the vertices with minimal y-values
            yMinVerticesXMin, yMin = np.amin(yMinVertices, axis=0)
            #Set the maximum acceptable x-value for x-value filter
            xMaxFilter = yMinVerticesXMin
            #Set the maximum acceptable y-value for y-value filter
            yMaxFilter = xMinVerticesYMin
            #Take the vertices which pass the x-value and y-value filters.
            frontIndices = np.where(np.logical_and(
                             vertices[:,0] <= xMaxFilter,
                             vertices[:,1] <= yMaxFilter))
            return frontIndices      

    def remove_frontindices(self, frontIndicesRelPoints):
        """Give the indices of the points without the indices of the front."""
        self.prunedPointsIndices = np.setdiff1d(self.prunedPointsIndices,
                                                frontIndicesRelPoints)
 
    def __init__(self, points, xReverse, yReverse):
        self.xReverse, self.yReverse = xReverse, yReverse
        self.pointsArray = np.array(map(np.array, points))
        numPoints = self.pointsArray.shape[0]
        self.prunedPointsIndices = np.arange(numPoints)
        #At least 3 points are needed to build a convex hull
        if numPoints < 3:           
            if numPoints == 0:
                raise ValueError("No Points passed to Pareto Front")
            else:   
                frontIndices = self.prunedPointsIndices
                self.frontsIndices.append(frontIndices)
                self.remove_frontindices(frontIndices)
        else:
            try:
                convexHull = scipy.spatial.ConvexHull(self.pointsArray)
            except scipy.spatial.qhull.QhullError:
                raise ValueError("All points are in a line.")
            #The indices of the points in the convex hull in the points array.
            hullIndicesRelPoints = convexHull.vertices
            #The coordinates of the points in the convex hull.
            hullVertices = self.pointsArray[hullIndicesRelPoints]
            #The indices of the points in the pareto front within the hull.
            frontIndicesRelHull = self.vertices_to_frontindices(hullVertices,
                                                self.xReverse, self.yReverse)
            #The indices of the points in the pareto front in the points array.
            frontIndicesRelPoints = hullIndicesRelPoints[frontIndicesRelHull]
            #Add the indices of the points in the pareto front to list.
            self.frontsIndices.append(frontIndicesRelPoints)
            #Remove the indices of the points in the pareto front from list.
            self.remove_frontindices(frontIndicesRelPoints)

    def build_nextfront(self):
        """Build the Pareto front of the points with the last front removed."""
        numPointsLeft = self.prunedPointsIndices.shape[0]
        if numPointsLeft < 3:
            if numPointsLeft == 0:
                return False
            else:
                frontIndicesRelPoints = self.prunedPointsIndices
                self.remove_frontindices(frontIndicesRelPoints)
                return True
        else:
            prunedPoints = self.pointsArray[self.prunedPointsIndices]
            convexHull = scipy.spatial.ConvexHull(prunedPoints)
            hullIndicesRelPrunedPoints = convexHull.vertices
            hullIndicesRelOriginalPoints = self.prunedPointsIndices[
                                            hullIndicesRelPrunedPoints]
            hullVertices = self.pointsArray[hullIndicesRelOriginalPoints]
            frontIndicesRelHull = self.vertices_to_frontindices(hullVertices,
                                                self.xReverse, self.yReverse)
            frontIndicesRelOriginalPoints = hullIndicesRelOriginalPoints[
                                          frontIndicesRelHull]
            self.frontsIndices.append(frontIndicesRelOriginalPoints)
            self.remove_frontindices(frontIndicesRelOriginalPoints)            
            return True          

