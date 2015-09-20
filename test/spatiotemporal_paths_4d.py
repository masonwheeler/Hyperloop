"""
Original Developer: Jonathan Ward
"""

# Standard Modules
import numpy as np

# Custom Modules:
import cacher
import comfort
import util

class SpatiotemporalPath4d(object):

    def compute_spatial_component_derivative(self, spatial_component_coords):
        spatial_component_derivative = util.numerical_derivative(
                        spatial_component_coords, self.time_checkpoints)
        return spatial_component_derivative

    def compute_velocities_components(self):
        x_component_coords = [tube_coord[0] for tube_coord in self.tube_coords]
        self.velocities_x_components = \
            self.compute_spatial_component_derivative(x_component_coords)
        y_component_coords = [tube_coord[1] for tube_coord in self.tube_coords]
        self.velocities_y_components = \
            self.compute_spatial_component_derivative(y_component_coords)
        z_component_coords = [tube_coord[2] for tube_coord in self.tube_coords]
        self.velocities_z_components = \
            self.compute_spatial_component_derivative(z_component_coords)

    def compute_accelerations_components(self):
        self.accelerations_x_components = \
        self.compute_spatial_component_derivative(self.velocities_x_components)
        self.accelerations_y_components = \
        self.compute_spatial_component_derivative(self.velocities_y_components)
        self.accelerations_z_components = \
        self.compute_spatial_component_derivative(self.velocities_z_components)
        
    def compute_comfort(self):
        velocities = np.transpose([self.velocities_x_components,
                                   self.velocities_y_components,
                                   self.velocities_z_components])        
        accelerations = np.transpose([self.accelerations_x_components,
                                   self.accelerations_y_components,
                                   self.accelerations_z_components])
        

        self.comfort_profile = [comfort.sperling_comfort_index(

    def __init__(self, velocity_profile, spatial_path_3d):
        self.time_checkpoints = velocity_profile.time_checkpoints
        #self.time_intervals = velocity_profile.time_intervals
        self.trip_time = velocity_profile.trip_time
        self.land_cost = spatial_path_3d.land_cost
        self.latlngs = spatial_path_3d.latlngs
        self.geospatials = spatial_path_3d.geospatials
        self.pylons = spatial_path_3d.pylons
        self.total_pylon_cost = spatial_path_3d.total_pylon_cost
        self.tube_coords = spatial_path_3d.tube_coords
        self.tube_cost = spatial_path_3d.tube_cost
        self.land_elevations = spatial_path_3d.land_elevations
        self.compute_velocities_components()
        self.compute_accelerations_components()


class SpatiotemporalPathsSet4d(object):

    def build_velocity_profiles_v1(self, spatial_path_3d):
        velocity_profile = self.velocity_builder(spatial_path_3d)
        velocity_profiles = [velocity_profile]
        return velocity_profiles

    def build_paths(self, spatial_path_3d, velocity_profiles):
        self.paths = [SpatiotemporalPath4d(velocity_profile, spatial_path_3d)
                      for velocity_profile in velocity_profiles]
    
    def __init__(self, spatial_path_3d, velocity_builder):
        self.velocity_builder = velocity_builder
        velocity_profiles = self.build_velocity_profiles_v1(spatial_path_3d)
        self.build_paths(spatial_path_3d, velocity_profiles)


class SpatiotemporalPathsSets4d(object):
    
    NAME = "spatiotemporal_paths_4d"
    FLAG = cacher.SPATIOTEMPORAL_PATHS_4D_FLAG
    
    def build_paths_sets(self, spatial_paths_3d):
        self.paths_sets = [SpatiotemporalPathsSet4d(spatial_path_3d,
                                                    self.velocity_builder)
                           for spatial_path_3d in spatial_paths_3d]

    def select_paths(self):
        paths_lists = [paths_set.paths for paths_set in self.paths_sets]
        paths = util.fast_concat(paths_lists)
        self.selected_paths = paths

    def __init__(self, spatial_paths_sets_3d, velocity_builder):
        self.velocity_builder = velocity_builder
        self.start = spatial_paths_sets_3d.start
        self.end = spatial_paths_sets_3d.end
        self.start_latlng = spatial_paths_sets_3d.start_latlng
        self.end_latlng = spatial_paths_sets_3d.end_latlng        
        self.undersampling_factor = spatial_paths_sets_3d.undersampling_factor
        self.build_paths_sets(spatial_paths_sets_3d.selected_paths)
        self.select_paths()


def get_spatiotemporal_paths_sets_4d(*args):
    spatiotemporal_paths_sets_4d = cacher.get_object(
                                        SpatiotemporalPathsSets4d.NAME,
                                        SpatiotemporalPathsSets4d,
                                        args,
                                        SpatiotemporalPathsSets4d.FLAG)
    return spatiotemporal_paths_sets_4d
