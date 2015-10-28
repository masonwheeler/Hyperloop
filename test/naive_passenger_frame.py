"""
Original Developer: Jonathan Ward
"""

# Standard Modules:
import numpy as np
import scipy.interpolate


class NaivePassengerFrame(object):

    def reparametrize_components_coords(self, tube_coords, 
                times_by_arc_length, cumulative_time_steps):
        (x_coords_by_arc_length, 
         y_coords_by_arc_length, 
         z_coords_by_arc_length) = np.transpose(tube_coords)
        x_coords_spline = scipy.interpolate.InterpolatedUnivariateSpline(
                             times_by_arc_length, x_coords_by_arc_length)
        y_coords_spline = scipy.interpolate.InterpolatedUnivariateSpline(
                             times_by_arc_length, y_coords_by_arc_length)
        z_coords_spline = scipy.interpolate.InterpolatedUnivariateSpline(
                             times_by_arc_length, z_coords_by_arc_length)
        #x_coords_by_time = x_coords_spline(cumulative_time_steps)
        #y_coords_by_time = y_coords_spline(cumulative_time_steps)
        #z_coords_by_time = z_coords_spline(cumulative_time_steps)
        #coords_by_time_vectors = np.transpose([x_coords_by_time,
        #                                       y_coords_by_time,
        #                                       z_coords_by_time])
        x_vels_spline = x_coords_spline.derivative(n=1)
        y_vels_spline = y_coords_spline.derivative(n=1)
        z_vels_spline = z_coords_spline.derivative(n=1)
        x_vels_by_time = x_vels_spline(cumulative_time_steps)
        y_vels_by_time = y_vels_spline(cumulative_time_steps)
        z_vels_by_time = z_vels_spline(cumulative_time_steps)
        vels_by_time_vectors = np.transpose([x_vels_by_time,
                                             y_vels_by_time,
                                             z_vels_by_time])
        x_accels_spline = x_coords_spline.derivative(n=2)
        y_accels_spline = y_coords_spline.derivative(n=2)
        z_accels_spline = z_coords_spline.derivative(n=2)
        x_accels_by_time = x_accels_spline(cumulative_time_steps)
        y_accels_by_time = y_accels_spline(cumulative_time_steps)
        z_accels_by_time = z_accels_spline(cumulative_time_steps)
        accels_by_time_vectors = np.transpose([x_accels_by_time,
                                             y_accels_by_time,
                                             z_accels_by_time])
        return [vels_by_time_vectors, accels_by_time_vectors]
  
    def compute_naive_frame(self, vels_vectors, accels_vectors):
        vels_norms = np.linalg.norm(vels_vectors, axis=1)
        tangent_vectors = vels_vectors / vels_norms[:,None]
        z_vector = np.array([0,0,1])
        z_vectors_list = [z_vector for i in range(vels_vectors.shape[0])]
        z_vectors = np.array(z_vectors_list)
        y_vectors = np.cross(z_vectors, tangent_vectors)
        change_of_basis_matrices = [np.linalg.inv(
                                        np.matrix.transpose(
                                            np.array([
                                                tangent_vectors[i],
                                                y_vectors[i],
                                                z_vectors[i]
                                                ])
                                            )
                                        )
                                    for i in range(vels_vectors.shape[0])]
        naive_frame_accels_vectors = [
            np.dot(change_of_basis_matrices[i], accels_vectors[i])
            for i in range(accels_vectors.shape[0])]
        return naive_frame_accels_vectors

    def __init__(self, tube_coords, times_by_arc_length, cumulative_time_steps):
        vels_vectors, accels_vectors = self.reparametrize_components_coords(
                    tube_coords, times_by_arc_length, cumulative_time_steps)
        self.cumulative_time_steps = cumulative_time_steps
        self.frame_accels_vectors = self.compute_naive_frame(
                                        vels_vectors, accels_vectors)
