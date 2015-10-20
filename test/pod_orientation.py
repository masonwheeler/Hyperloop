"""
Original Developer: Jonathan Ward
"""


class NaivePodOrientation(object):

    def __init__(self):


class FrenetSerretPodOrientation(object):

    def compute_velocities_vectors(self, tube_coords, time_checkpoints):
        x_coords, y_coords, z_coords = np.transpose(tube_coords)
        x_velocities = self.compute_velocity(x_coords, time_checkpoints)
        y_velocities = self.compute_velocity(y_coords, time_checkpoints)
        z_velocities = self.compute_velocity(z_coords, time_checkpoints)
        velocities_vectors = np.tranpose([x_velocities, y_velocities, 
                                                        z_velocities])
        return velocities_vectors

    def __init__(self):
