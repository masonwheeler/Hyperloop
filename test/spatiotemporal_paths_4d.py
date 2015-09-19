"""
Original Developer: Jonathan Ward
"""

import numpy as np

import comfort
import util

class SpatiotemporalPath4d(object):

    def compute_spatial_component_derivative(self, spatial_component_coords):
        spatial_component_derivative = util.numerical_derivative(
                        spatial_component_coords, self.time_check_points)
        return spatial_component_derivative

    def compute_spatial_velocities(self):
        x_component_coords = [tube_coord[0] for tube_coord in self.tube_coords]
        self.x_component_velocities = self.compute_spatial_component_derivative(
                                                           x_component_coords)
        y_component_coords = [tube_coord[1] for tube_coord in self.tube_coords]
        self.y_component_velocities = self.compute_spatial_component_derivative(
                                                           y_component_coords)
        z_component_coords = [tube_coord[2] for tube_coord in self.tube_coords]
        self.z_component_velocities = self.compute_spatial_component_derivative(
                                                           z_component_coords)

    def compute_spatial_accelerations(self):
        self.x_component_accels = self.compute_spatial_component_derivative(
                                                self.x_component_velocities)
        self.y_component_accels = self.compute_spatial_component_derivative(
                                                self.y_component_velocities)
        self.z_component_accels = self.compute_spatial_component_derivative(
                                                self.z_component_velocities)
        
    def compute_comfort(self):
        

    def __init__(self, velocity_profile, spatial_path_3d):
        self.time_check_points = velocity_profile.time_check_points
        self.time_intervals = velocity_profile.time_intervals
        self.land_cost = spatial_path_3d.land_cost
        self.latlngs = spatial_path_3d.latlngs
        self.geospatials = spatial_path_3d.geospatials
        self.pylons = spatial_path_3d.pylons
        self.total_pylon_cost = spatial_path_3d.total_pylon_cost
        self.tube_coords = spatial_path_3d.tube_coords
        self.tube_cost = spatial_path_3d.tube_cost
        self.land_elevations = spatial_path_3d.land_elevations


class SpatiotemporalPathsSet4d(object):

    def build_velocity_profiles_v1(self):
        velocity_profile = self.velocity_builder(spatial_path_3d)
        self.velocity_profiles[velocity_profile]

    def build_paths(self, spatial_path_3d):
        self.paths = [Path4d(velocity_profile, spatial_path_3d)
                      for velocity_profile in self.velocity_profiles]
    
    def __init__(self, spatial_path_3d, velocity_builder):
        self.velocity_builder = velocity_builder
        self.build_velocity_profiles_v1()
        self.build_paths()


class SpatiotemporalPathsSets4d(object):
    
    NAME = "spatiotemporal_paths_4d"
    FLAG = cacher.SPATIOTEMPORAL_PATHS_4D
    
    def build_paths_sets(self, spatial_paths_3d):
        self.paths_sets = [SpatiotemporalPathsSet4d(spatial_path_3d,
                                                    self.velocity_builder)
                           for spatial_path_3d in spatial_paths_3d]

    def select_paths(self):
        paths_lists = [paths_set.path for paths_set in self.paths_sets]
        paths = util.fast_oncat(paths_lists)
        self.selected_paths = paths

    def __init__(self, spatial_paths_sets_3d):
        self.start = spatial_paths_sets_3d.start
        self.end = spatial_paths_sets_3d.end
        self.start_latlng = spatial_paths_sets_3d.start_latlng
        self.end_latlng = spatial_paths_sets_3d.end_latlng        
        self.velocity_builder = spatial_paths_sets_3d.velocity_builder
        self.undersampling_factor = spatial_paths_set_3d.undersampling_factor
        self.build_paths_sets(spatial_paths_sets_3d.selected_paths)
        self.select_paths()


def get_spatiotemporal_paths_sets_4d(*args):
    spatiotemporal_paths_sets_4d = cacher.get_object(
                                        SpatiotemporalPathsSets4d.NAME,
                                        SpatiotemporalPathsSets4d,
                                        args,
                                        SpatiotemporalPathsSets.FLAG)
    return spatiotemporal_paths_sets_4d
