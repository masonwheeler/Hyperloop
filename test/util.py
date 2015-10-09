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

NDIGITS = 6  # the number of digits used for rounding

def round_num(num):
    """Rounds number to predefined number of places"""
    return round(num, NDIGITS)

def round_nums(nums):
    """Rounds a list of numbers"""
    return [round_num(num) for num in nums]

def round_points(points):
    """
    Rounds the values in each point in a list of points
    """
    return [round_nums(point) for point in points]

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


# List Pair Operations:

def smart_concat(list_a, list_b):
    """Connects two lists without duplicating shared boundary point"""
    new_list = list_a + list_b[1:]
    return new_list

def smart_concat_array(array_a, array_b):
    """Connects two lists without duplicating shared boundary point"""
    new_array = np.concatenate((array_a, array_b[1:]))
    return new_array

def offset_concat(list_a, list_b):
    offset = list_a[-1]
    shifted_list_b = [val + offset for val in list_b]
    new_list = smart_concat(list_a, shifted_list_b)
    return new_list

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

def build_grid(start_point, end_point, spacing):
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

def sample_list(in_list, num_samples):
    fractions = [float(i)/float(num_samples) for i in range(num_samples)]
    difference = in_list[-1] - in_list[0]
    samples = [fraction * difference + in_list[0] for fraction in fractions]
    return samples

def bisect_list(in_list):
    bisected_list = sample_list(in_list, 3)
    return bisected_list

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

