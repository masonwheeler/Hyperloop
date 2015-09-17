"""
Port of match_landscape for testing
"""

import parameters
import config

def sort_velocities_indices(velocities_indices):    
    sorted_velocities_indices = sorted(velocities_indices,
                              key=lambda i: velocities[i])
    sorted_interior_velocities_indices = [index + 1 for index in
                                          sorted_velocities_indices]
    return sorted_interior_velocities_indices

def get_route_max_velocities():
    return route_max_velocities

def test_velocities_pair_v1(velocity_a, arc_length_a, velocity_b, arc_length_b):
    velocity_difference = velocity_b - velocity_a
    arc_length_difference = arc_length_a - arc_length_b
    mean_velocity = (velocity_a + velocity_b) / 2.0
        
def test_velocity_indices_pair(velocity_index_a, velocity_index_b,
                      index_pairs_tested, velocities, arc_lengths):
    if index_pairs_tested[velocity_index_a][velocity_index_b]:
        return True
    else:
        index_pairs_tested[velocity_index_a][velocity_index_b] = True
        index_pairs_tested[velocity_index_b][velocity_index_a] = True
        velocity_a = velocities[velocity_index_a]
        arc_length_a = arc_lengths[velocity_index_a]        
        velocity_b = velocities[velocity_index_b]
        arc_length_b = arc_lengths[velocity_index_b]
        are_velocities_compatible = test_velocities_pair_v1(velocity_a,
                                arc_length_a, velocity_b, arc_length_b)
        return are_velocities_compatible
    
def test_velocity_index(velocity_index, selected_velocities_indices):
    position_of_trial_index = util.sorted_insert(velocity_index,
                              selected_velocities_indices)
    backward_index = selected_velocities_indices[posiition_of_trial_index - 1]
    trial_index = selected_velocities_indices[posiition_of_trial_index]
    forward_index = selected_velocities_indices[posiition_of_trial_index + 1]
    backward_compatibility = test_velocity_indices_pair(backward_index,
                                                           trial_index)
    forward_compatibility = test_velocity_indices_pair(backward_index,
                                                           trial_index)
    velocity_index_compatible = backward_compatibility and forward_compatiblity
    selected_velocities_indices.pop(position_of_trial_index)
    return velocity_index_compatible

def add_compatible_velocity_to_profile(sorted_interior_velocities_indices,
                                             selected_velocities_indices):
    for i in range(len(sorted_interior_velocities_indices)):
        trial_index = sorted_inerior_velocities_indices[i]
        if test_velocity_index(trial_index, selected_velocities_indices):
            trial_index = sorted_interior_velocities_indices.pop(i)
            util.sorted_insert(trial_index, selected_velocities_indices)
            return True
    return False    

def build_velocity_profile(arc_lengths, velocities)
    selected_velocities_indices = []
    start_velocity_index = 0
    selected_velocities_indices.append(start_velocity_index)
    final_velocity_index = len(velocities) - 1
    selected_velocities_indices.append(final_velocity_index)
    interior_velocities = velocities[1: len(velocities) - 1]
    sorted_interior_velocities_indices = sort_velocities_indices(
                                             interior_velocities)
    index_pairs_tested = [[0 for i in range(len(velocities))]
                             for j in range(len(velocities))]
    while True:
        added_compatible_velocity = add_compatible_velocity_to_profile(
                                    sorted_interior_velocities_indices,
                                           selected_velocities_indices)
        if added_compatible_velocity:
            pass
        else:
            break
    selected_arc_lengths = [arc_lengths[index] for index
                            in selected_velocities_indices]
    selected_velocities = [velocities[index] for index
                           in selected_velocities_indices]
    return [selected_arc_lengths, selected_velocities]        
    

