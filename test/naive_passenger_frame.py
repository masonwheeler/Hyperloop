"""
Original Developer: Jonathan Ward
"""


class NaivePassengerFrame(object):

    def compute_derivative(self, x_vals, y_vals):
        y_diffs = np.ediff1d(y_vals)
        x_diffs = np.ediff1d(x_vals)
        quotients = np.divide(y_diffs, x_diffs)
        quotients_a = quotients[:-1]
        quotients_b = quotients[1:]
        mean_quotients = (quotients_a + quotients_b) / 2.0
        derivative = np.empty(x_vals.shape[0])
        derivative[1:-1] = mean_quotients
        derivative[0] = quotients[0]
        derivative[-1] = quotients[-1]
        return derivative

    def compute_vels_vectors(self, tube_coords, time_checkpoints):
        x_coords, y_coords, z_coords = np.transpose(tube_coords)
        x_vels = self.compute_derivative(time_checkpoints, x_coord)
        y_vels = self.compute_derivative(time_checkpoints, y_coord)
        z_vels = self.compute_derivative(time_checkpoints, z_coord)
        vels_vectors = np.transpose([x_vels, y_vels, z_vels])
        return vels_vectors

    def compute_accels_vectors(self, vels_vectors, time_checkpoints):
        x_vels, y_vels, z_vels = np.tranpose(vels_vectors)
        x_accels = self.compute_derivative(time_checkpoints, vels_vectors)
        y_accels = self.compute_derivative(time_checkpoints, vels_vectors)
        z_accels = self.compute_derivative(time_checkpoints, vels_vectors)
        accels_vectors = np.transpose([x_accels, y_accels, z_accels])
        return accels_vectors

    def compute_naive_frame(self, vels_vectors, accels_vectors):
        vels_norms = np.linalg.norm(vels_vectors, axis=0)
        tangent_vectors = np.divide(vels_vectors, vels_norms)
        z_vector = np.array([0,0,1])
        z_vectors_list = [z_vector for i in range(vels_vectors.shape[0])]
        z_vectors = np.array(z_vectors_list)
        y_vectors = np.cross(z_vectors, tangent_vectors)
        change_of_basis_matrices = [np.linalg.inv(
                                        np.matrix.tranpose(
                                            np.array(
                                                tangent_vectors[i],
                                                y_vectors[i],
                                                z_vectors[i],
                                                )
                                            )
                                        )
                                    for i in range(vels_vectors.shape[0])]
        naive_frame_accels_vectors = [
            np.dot(change_of_basis_matrices[i], accels_vectors[i])
            for i in range(accels_vectors.shape[0])]
        return naive_frame_accels_vectors

    def __init__(self, tube_coords, time_checkpoints):
        vels_vectors = self.compute_vels_vectors(tube_coords, time_checkpoints)
        accels_vectors = self.compute_accels_vectors(vels_vectors,
                                                     time_checkpoints)
        self.frame_accels_vectors = self.compute_naive_frame(
                                        vels_vectors, accels_vectors)


