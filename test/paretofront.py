"""
Original Developer: Jonathan Ward
Purpose of Modules: To compute the 2d Pareto Front.
Last Modified: 7/28/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To add comments.
"""
# pylint: disable=E1101, R0914

# Standard Modules:
import scipy
import numpy as np


class ParetoFront(object):
    """
    Computes nested Pareto Frontiers of points in 2d.

    Calculates the Convex Hull of the set of points using qhull,
    then computes the Pareto Front of those points.
    """
    points_array = []  # Numpy array containing original points.
    pruned_points_indices = []  # Contains the indices of the pruned points.
    fronts_indices = []  # Contains the indices of the points in each fronts.

    @staticmethod
    def vertices_to_frontindices(vertices):
        """
        Computes the Pareto front given the vertices of the convex hull.

        If x_reverse is set to True then the Pareto front minimizes x-values.
        If y_reverse is set to True then the Pareto front minimizes y-values.
        """
        x_min, y_min = np.amin(vertices, axis=0)
        # The vertices with x-values equal to x-min
        x_min_vertices = vertices[np.where(vertices[:, 0] == x_min)]
        # The vertices with y-values equal to y-min
        y_min_vertices = vertices[np.where(vertices[:, 1] == y_min)]

        # To find the minimum y-value of the vertices with minimal x-values
        _, y_max_filter = np.amin(x_min_vertices, axis=0)
        # To find the minimum x-value of the vertices with minimal y-values
        x_max_filter, _ = np.amin(y_min_vertices, axis=0)
        # Take the vertices which pass the x-value and y-value filters.
        front_indices_tuple = np.where(np.logical_and(
            vertices[:, 0] <= x_max_filter,
            vertices[:, 1] <= y_max_filter))
        front_indices = front_indices_tuple[0]
        reduced_vertices = vertices[front_indices]
        sorted_reduced_vertices_indices = np.argsort(reduced_vertices[:, 0])
        sorted_front_indices = front_indices[
                 sorted_reduced_vertices_indices]
        sorted_reduced_vertices = reduced_vertices[
                       sorted_reduced_vertices_indices]
        selected_indices = [0]
        num_vertices = sorted_reduced_vertices.shape[0]
        for i in range(num_vertices - 1):
            vertex_a = sorted_reduced_vertices[i]
            vertex_b = sorted_reduced_vertices[i + 1]
            if vertex_b[1] < vertex_a[1]:
               selected_indices.append(i + 1)
        selected_front_indices = sorted_front_indices[selected_indices]
        return selected_front_indices

    def remove_front_indices(self, front_indices_rel_points):
        """Gives the indices of the points without the indices of the front."""
        print "num points before: " + str(len(self.pruned_points_indices))
        intersection = np.intersect1d(self.pruned_points_indices,
                                      front_indices_rel_points)
        if intersection.shape[0] == 0:
            print "empty intersection"
            raise IndexError
        else:
            self.pruned_points_indices = np.setdiff1d(self.pruned_points_indices,
                                                  front_indices_rel_points)
            print "num points after: " + str(len(self.pruned_points_indices))

    @staticmethod
    def check_linear(points_array):
        x_vals, y_vals = np.transpose(points_array)
        are_x_vals_identical = np.all(x_vals==x_vals[0])
        are_y_vals_identical = np.all(y_vals==y_vals[0])
        are_points_linear = are_x_vals_identical or are_y_vals_identical
        return are_points_linear

    @staticmethod
    def get_linear_min(points_array):
        x_vals, y_vals = np.transpose(points_array)
        are_x_vals_identical = np.all(x_vals==x_vals[0])
        are_y_vals_identical = np.all(y_vals==y_vals[0])
        if are_x_vals_identical:
            min_index = np.argmin(y_vals)
        if are_y_vals_identical:
            min_index = np.argmin(x_vals)
        return [min_index]        

    @staticmethod
    def remove_duplicates(points_array):
        """Gives the indices of the unique points."""
        # reshapes the points array into an array of tuples
        tuples_array = np.ascontiguousarray(points_array).view(
            np.dtype((np.void,
            points_array.dtype.itemsize * points_array.shape[1])))
        # selects the indices of the unique tuples.
        _, unique_indices = np.unique(tuples_array, return_index=True)
        sorted_unique_indices = sorted(unique_indices)
        return sorted_unique_indices

    def __init__(self, points):
        self.fronts_indices = []
        # Raw points array may contain duplicates
        raw_points_array = np.array([np.array(point) for point in points])
        # The indices of the unique points in the raw points array.
        # The unique points in the raw points array.
        self.points_array = raw_points_array
        # The number of rows in the points array
        num_points = self.points_array.shape[0]
        # set the indices of the pruned points as the indices of all points
        self.pruned_points_indices = np.arange(num_points)
        # At least 3 points are needed to build a convex hull
        if num_points < 3:
            # if there are no points, raise a value error.
            if num_points == 0:
                print "No points passed to Pareto Front"
                raise ValueError("No Points passed to Pareto Front")
            else:
                # if there are 1 or 2 points, add these to the fronts
                front_indices = self.pruned_points_indices
                self.fronts_indices.append(front_indices.tolist())
                self.remove_frontindices(front_indices)
        else:
            are_points_linear = ParetoFront.check_linear(self.points_array)
            if are_points_linear:                      
                # if the points are linear, just add them all to the fronts.
                linear_min_index = ParetoFront.get_linear_min(self.points_array)
                front_indices = linear_min_index               
                self.fronts_indices.append(front_indices)
                self.remove_front_indices(front_indices)
            else:
                # If there are enough points, try to build a convex hull.
                try:
                    convex_hull = scipy.spatial.ConvexHull(self.points_array)
                # If convex hull not built, raise a value error.
                except scipy.spatial.qhull.QhullError:
                    print "all points are in a line."
                    raise ValueError("All points are in a line.")
                # If another strange error occurs, record that.
                except ValueError:
                    print "Qhull encountered other error"
                    raise ValueError("Qhull encountered other error")
                # The indices of the convex hull vertices in the points array
                hull_indices = convex_hull.vertices
                # The vertices in the convex hull.
                hull_vertices = self.points_array[hull_indices]
                # The indices of the points in the pareto front in the hull array.
                front_indices_rel_hull = ParetoFront.vertices_to_frontindices(
                                                                hull_vertices)
                # The indices of the points in the pareto front in the points
                # array.
                front_indices_rel_points = hull_indices[front_indices_rel_hull]
                # Add the indices of the points in the pareto front to list.
                self.fronts_indices.append(front_indices_rel_points.tolist())
                # Remove the indices of the points in the pareto front from list.
                self.remove_frontindices(front_indices_rel_points)

    def build_nextfront(self):
        """
        Build the Pareto front of the points with the last front removed

        If the next front is successfully built return True, otherwise False.
        Since points array does not have duplicates,
        the pruned points array does not have duplicates.
        """
        # Initialize the points which have not been in a front yet
        pruned_points = self.points_array[self.pruned_points_indices]
        # The number of rows in the pruned points array
        num_points_left = pruned_points.shape[0]
        # At least 3 points are needed to build a convex hull
        if num_points_left < 3:
            # If there are no points, record failure
            if num_points_left == 0:
                return False
            else:
                # If there are 1 or 2 points, add them to the front
                front_indices_rel_points = self.pruned_points_indices
                self.fronts_indices.append(front_indices_rel_points.tolist())
                self.remove_front_indices(front_indices_rel_points)
                return True
        else:
            are_points_linear = ParetoFront.check_linear(self.points_array)
            if are_points_linear:
                # if the points are linear, just add them all to the fronts.
                linear_min_index = ParetoFront.get_linear_min(pruned_points)
                front_indices = linear_min_index               
                self.fronts_indices.append(front_indices)
                self.remove_front_indices(front_indices)
                return True
            else:
                # If there are enough points, try to build a convex hull
                try:
                    convex_hull = scipy.spatial.ConvexHull(pruned_points)
                # if convex hull not built, raise a value error.
                except scipy.spatial.qhull.QhullError:
                    print "all points are in a line."
                    raise ValueError("All points are in a line.")
                # If another strange error occurs, record that.
                except ValueError:
                    print "Qhull encountered other error"
                    raise ValueError("Qhull encountered other error")
                # The indices of the vertices in the convex hull
                # relative to the pruned points array
                hull_indices_rel_pruned_points = convex_hull.vertices
                # The indices of the vertices in the convex hull
                # relative to the points array
                hull_indices_rel_points = self.pruned_points_indices[
                    hull_indices_rel_pruned_points]
                # The vertices in the convex hull
                hull_vertices = self.points_array[hull_indices_rel_points]
                # The indices of the points in the front
                # relative to the convex hull.
                front_indices_rel_hull = ParetoFront.vertices_to_frontindices(
                             hull_vertices, self.x_reverse, self.y_reverse)
                # The indices of the points in the front
                # relative to the points array.
                front_indices_rel_points = hull_indices_rel_points[
                    front_indices_rel_hull]
                # Add the indices of the points in the pareto front to list.
                front_indices_list = front_indices_rel_points.tolist()
                self.fronts_indices.append(front_indices_list)
                # Remove the indices of the points in the pareto front from list.
                self.remove_front_indices(front_indices_rel_points)
                return True
