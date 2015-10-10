"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import numpy as np

# Custom Modules:
import util

def distance_along_edge_to_point(edge, distance_along_edge):
    edge_start, edge_end = edge
    edge_vector = util.subtract(edge_end, edge_start)
    edge_length = util.norm(edge_vector)
    scale_factor = distance_along_edge / edge_length
    scaled_vector = util.scale(scale_factor, edge_vector)
    point = util.add(scaled_vector, edge_start)
    return point

def sample_edge(edge, sample_spacing, distance_along_edge, start_arc_length):
    edge_length = util.norm(util.edge_to_vector(edge))
    edge_points = []
    edge_arc_lengths = []
    while distance_along_edge <= edge_length:
        point_arc_length = distance_along_edge + start_arc_length
        edge_arc_lengths.append(point_arc_length)
        point = distance_along_edge_to_point(edge, distance_along_edge)
        edge_points.append(point)
        distance_along_edge += sample_spacing
    distance_along_edge -= edge_length
    return [edge_points, edge_arc_lengths, distance_along_edge, edge_length]
    
def sample_edges(edges, sample_spacing):
    distance_along_edge = 0
    start_arc_length = 0
    points = []
    arc_lengths = []
    for edge in edges:
        edge_points, edge_arc_lengths, distance_along_edge, edge_length = \
        sample_edge(edge, sample_spacing, distance_along_edge, start_arc_length)
        points += edge_points
        arc_lengths += edge_arc_lengths
        start_arc_length += edge_length
    last_arc_length = start_arc_length
    return [points, arc_lengths, last_arc_length]

def sample_path_points_v2(path_points, path_sample_spacing):
    path_edges = util.to_pairs(path_points)
    sampled_path_points, sampled_arc_lengths, last_arc_length = \
                    sample_edges(path_edges, path_sample_spacing)
    last_point = path_points[-1]
    sampled_arc_lengths.append(last_arc_length)
    sampled_path_points.append(last_point)
    return [sampled_path_points, sampled_arc_lengths]


def sample_points_pair(start_point, end_point, step, offset):
    print "start point: "
    print start_point
    print "end point: " 
    print end_point
    vector = end_point - start_point
    print "vector: "
    print vector
    x_diff, y_diff = vector
    vector_length = np.linalg.norm(vector)
    cos, sin = x_diff / vector_length, y_diff / vector_length
    x_offset, y_offset = offset * cos, offset * sin
    x_step, y_step = step * cos, step * sin
    start_x, start_y = start_point
    end_x, end_y = end_point
    offset_start_x, offset_start_y = start_x + x_offset, start_y + y_offset
    x_samples = np.arange(offset_start_x, end_x, x_step)
    y_samples = np.arange(offset_start_y, end_y, y_step)
    distances = np.arange(offset, vector_length, step)
    x_remainder = end_x - x_samples[-1]
    y_remainder = end_y - y_samples[-1]
    length_remainder = np.hypot(x_remainder, y_remainder)
    offset = step - length_remainder
    samples = np.transpose([x_samples, y_samples])
    return [samples, distances, offset]

def sample_path_points(path_points, step):
    offset = 0
    distance_along_path = 0
    path_distances = np.array([])
    path_samples = np.array([]).reshape(0,2)
    for i in range(path_points.shape[0] - 1):
        samples, distances, offset = sample_points_pair(path_points[i],
                                   path_points[i + 1], step, offset)
        distances += distance_along_path
        distance_along_path = distances[-1]
        path_samples = np.concatenate((path_samples, samples))
        path_distances = np.concatenate((path_distances, distances))
    return [path_samples, distances]
        
