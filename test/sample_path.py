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

def sample_path_points(path_points, path_sample_spacing):
    path_edges = util.to_pairs(path_points)
    sampled_path_points, sampled_arc_lengths, last_arc_length = \
                    sample_edges(path_edges, path_sample_spacing)
    last_point = path_points[-1]
    sampled_arc_lengths.append(last_arc_length)
    sampled_path_points.append(last_point)
    sampled_path_points_array = np.array([np.array(point) for point
                                          in sampled_path_points])
    sampled_arc_lengths_array = np.array(sampled_arc_lengths)
    return [sampled_path_points_array, sampled_arc_lengths_array]

