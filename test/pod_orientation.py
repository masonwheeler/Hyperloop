"""
Original Developer: Jonathan Ward
"""


class NaivePodOrientation(object):

    def __init__(self):


class FrenetSerretPodOrientation(object):

    def compute_velocities_vectors(self, tube_coords, time_checkpoints):
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

    def compute_frenet_serret_frame(self, vels_vectors, accels_vectors):
        vels_norms = np.linalg.norm(vels_vectors, axis=0)
        tangent_vectors = np.divide(vels_vectors, vels_norms)
        accels_vels_cross_prods = np.cross(accels_vectors, vels_vectors)
        vels_accels_cross_prods = np.cross(vels_vectors, accels_vectors)
        tangent_vectors_derivs = np.cross(vels_vectors, accels_vels_cross_prods)
        tangent_vectors_derivs_norms = np.linalg.norm(tangent_vectors_derivs,
                                                      axis=0)
        normal_vectors = np.divide(tangent_vectors_derivs, 
                                   tangent_vectors_derivs_norms)
        vels_accels_cross_prods_norms = np.linalg.norm(vels_accels_cross_prods,
                                                       axis=0)
        binormal_vectors = np.divide(vels_accels_cross_prods,
                                     vels_accels_cross_prods_norms)
        change_of_basis_matrices = [np.linalg.inv(
                                        np.matrix.tranpose(
                                            np.array(
                                                tangent_vectors[i],
                                                normal_vectors[i],
                                                binormal_vectors[i])
                                                )
                                        )
                                    for i in range(len(vels_vectors))]
        frenet_serret_accels_vectors = [
            np.dot(change_of_basis_matrices[i], accels_vectors[i])
            for i in range(len(accels_vectors))]
        return frenet_serret_accels_vectors        

    def __init__(self, vels_vectors, accels_vectors):






















