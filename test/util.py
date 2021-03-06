"""
Original Developer: Jonathan Ward
Purpose of Module: To provide a suite of utility function for the algorithm.
Last Modified: 7/30/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added docstrings
"""

# Standard Modules
import math
import numpy as np
import itertools
import operator

# Our Modules
import config

#pylint: disable=C0103, E1101, W0142, W0141

# Points Operations:

def round_nums(nums, ndigits):
    """Rounds a list of numbers"""
    return [round(num, ndigits) for num in nums]

def round_points(points, ndigits):
    """
    Rounds the values in each point in a list of points
    """
    return [round_nums(point, ndigits) for point in points]

def to_pairs(points):
    """
    Converts a list of points to a list of pairs of points
    """
    pairs = [points[i:i + 2] for i in range(len(points) - 1)]
    return pairs

# Pair Operations:

def swap_pair(pair):
    """
    Swaps a pair of points
    """
    return [pair[1], pair[0]]

def swap_pairs(pairs):
    """
    Swaps pairs of points
    """
    return [[pair[1], pair[0]] for pair in pairs]

# List of Lists Operations:

def fast_concat(list_of_lists):
    """Concatenates a list of lists"""
    concatenated = itertools.chain.from_iterable(list_of_lists)
    return list(concatenated)

def list_of_lists_len(list_of_lists):
    """gets total length of a list of lists"""
    return sum(map(len, list_of_lists))

def glue_list_of_arrays(list_of_arrays):
    glued_arrays = list_of_arrays[0]
    for array in list_of_arrays[1:]:
        glued_arrays = glue_array_pair(glued_arrays, array)
    return glued_arrays

# List Pair Operations:

def glue_list_pair(list_a, list_b):
    """Connects two lists without duplicating shared boundary point"""
    glued_list = list_a + list_b[1:]
    return glued_list

def glue_array_pair(array_a, array_b):
    """Connects two lists without duplicating shared boundary point"""
    glued_array = np.concatenate((array_a, array_b[1:]))
    return glued_array

def shift_and_glue_list_pair(list_a, list_b):
    offset = list_a[-1]
    shifted_list_b = [val + offset for val in list_b]
    glued_list = glue_list_pair(list_a, shifted_list_b)
    return glue_list

def shift_and_glue_array_pair(array_a, array_b):
    offset = array_a[-1]
    shifted_array_b = array_b + offset
    glued_array = glue_array_pair(array_a, shifted_array_b)
    return glued_array

# Vector Operations:

def safe_operation(operation, vector_a, vector_b):
    """Wrapper function for safe vector operations
    """
    if len(vector_a) == len(vector_b):
        return map(operation, vector_a, vector_b)
    else:
        print vector_a
        print vector_b
        raise ValueError("Mismatched vector lengths.")

def add(vector_a, vector_b):
    """Adds a pair of vectors
    """
    return safe_operation(operator.add, vector_a, vector_b)

def subtract(vector_a, vector_b):
    """Subtracts the second vector from the first
    """
    return safe_operation(operator.sub, vector_a, vector_b)

def entry_multiply(vector_a, vector_b):
    """Multiplies a pair of vectors entry by entry
    """
    return safe_operation(operator.mul, vector_a, vector_b)

def scale(scalar, vector):
    """Multiply each element of the vector by the given scale
    """
    return [element * scalar for element in vector]

def norm(vector):
    """Computes the norm of the given vector
    """
    return math.sqrt(sum([x**2 for x in vector]))

def vector_to_angle(vector):
    """Computes the angle of the given vector
    """
    x_val, y_val = vector
    angle = math.degrees(math.atan2(y_val, x_val))
    return angle

# Sampling Operations:

def sample_vector(vector, spacing):
    """Sample points from the interior of a vector at a regular spacing
    """
    effective_scale = norm(vector) / spacing
    unit_vector = scale(1.0 / effective_scale, vector)
    num_points = int(math.ceil(effective_scale))
    point_indices = range(num_points)
    point_distances = [spacing * index for index in point_indices]
    point_vectors = [scale(index, unit_vector) for index in point_indices]
    return [point_vectors, point_distances]

def build_grid(start_point, end_point, step):    
    """Builds a grid of points between the start and end point.
    """
    vector = end_point - start_point
    x_diff, y_diff = vector
    vector_length = np.linalg.norm(vector)
    x_step = (x_diff / vector_length) * step
    y_step = (y_diff / vector_length) * step
    start_x, start_y = start_point
    end_x, end_y = end_point
    x_grid = np.arange(start_x, end_x, x_step)
    x_grid = np.append(x_grid, end_x)
    y_grid = np.arange(start_y, end_y, y_step)
    y_grid = np.append(y_grid, end_y)
    grid = np.transpose([x_grid, y_grid])
    distances = np.arange(0, vector_length, step)
    distances = np.append(distances, vector_length)
    return [grid, distances]

def build_grid_v2(start_point, end_point, spacing):
    """Builds a grid of points between the start and end point.
    """
    vector = subtract(end_point, start_point)
    length = norm(vector)
    if length < spacing:
        return [[start_point, end_point], [0, length]]
    else:
        point_vectors, point_distances = sample_vector(vector, spacing)
        point_vectors.append(vector)
        point_distances.append(length)
        grid = [add(point_vector, start_point)
                for point_vector in point_vectors]
        return [grid, point_distances]

def sample_length(length, spacing):
    """sample values within a given length at a regular spacing
    """
    num_points = int(length / spacing)
    values = [index * spacing for index in range(num_points + 1)]
    return values

def build_grid_1d(start_value, end_value, spacing):
    """Build a 1d grid of points in a given interval
    """
    length = end_value - start_value
    values = sample_length(length, spacing)
    if values == None:
        return None
    else:
        grid = [value + start_value for value in values]
        return grid

# Edge Operations:

def edge_to_vector(edge):
    """Convert a given edge to a vector.
    """
    edge_start, edge_end = edge
    edge_vector = subtract(edge_end, edge_start)
    return edge_vector

# String Operations:

def smart_print(string):
    """Print the input string if verbose mode is turned on.
    """
    if config.VERBOSE_MODE:
        print string

