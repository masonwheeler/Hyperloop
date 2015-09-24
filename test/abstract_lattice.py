"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To implement the AbstractLattice class and accompanying classes.

Last Modified:
    09/13/15

Last Modified By:
    Jonathan Ward

Last Modification Purpose:
    Moved get plottable lattice to subclasses
"""

#Standard Modules:
import numpy as np

class AbstractPoint(object):
    """Abstract object that represents a point.

    Attributes:
        point_id (int): Unique identifier for each point.
        abstract_x_coord (int): The x coordinate of the point with
                               relative to the lattice of points.
        abstract_y_coord (int): The y coordinate of the point with
                               relative to the lattice of points.
        physical_x_coord (float): The x coordinate of the point
                                in physical units.
        physical_y_coord (float): The y coordinate of the point
                                in physical units.

    """

    def __init__(self, point_id, abstract_x_coord, abstract_y_coord,
                 physical_x_coord, physical_y_coord):
        self.point_id = point_id
        self.abstract_x_coord = abstract_x_coord
        self.abstract_y_coord = abstract_y_coord
        self.physical_x_coord = physical_x_coord
        self.physical_y_coord = physical_y_coord


class AbstractSlice(object):

    def __init__(self, abstract_x_coord, slice_bounds, start_id,
                                         slice_points_builder):
        self.points, self.end_id = slice_points_builder(abstract_x_coord,
                                                 slice_bounds, start_id)

    def get_physical_x_coords(self):
        physical_x_coords = [point.physical_x_coord for point in self.points]
        return physical_x_coords

    def get_physical_y_coords(self):
        physical_y_coords = [point.physical_y_coord for point in self.points]
        return physical_y_coords


class AbstractLattice(object):

    def __init__(self, slices_bounds, slice_builder):
        self.slices = []
        start_id = 0
        abstract_x_coord = 0
        for slice_bounds in slices_bounds:
            new_slice = slice_builder(abstract_x_coord, slice_bounds, start_id)
            self.slices.append(new_slice)
            start_id = new_slice.end_id
            abstract_x_coord += 1

    def get_plottable_lattice(self, color_string):
        slices_physical_x_coords = [eachSlice.get_physical_x_coords()
                                    for eachSlice in self.slices]
        slices_physical_y_coords = [eachSlice.get_physical_y_coords()
                                    for eachSlice in self.slices]
        physical_x_coords = util.fast_concat(slices_physical_x_coords)
        physical_y_coords = util.fast_concat(slices_physical_y_coords)
        physical_x_coords_array = np.array(physical_x_coords)
        physical_y_coords_array = np.array(physical_y_coords)
        lattice_points = [physical_x_coords_array, physical_y_coords_array]
        plottable_lattice = [lattice_points, color_string]
        return plottable_lattice

