"""
Original Developer: Jonathan Ward
"""

# Standard Modules
import numpy as np

# Custom Modules:
import cacher
##import comfort
import paretofront
import util


class SpatiotemporalPath4d(object):
        
    def compute_comfort(self, velocity_profile):
        self.comfort_profile = []
        self.comfort_rating = 0

    def __init__(self, velocity_profile, spatial_path_3d):
        #self.trip_time = velocity_profile.trip_time
        #self.speed_profile = velocity_profile.speed_profile
        #self.scalar_acceleration_profile = \
        #    velocity_profile.scalar_acceleration_profile
        self.speed_profile = []
        self.scalar_acceleration_profile = []
        self.latlngs = spatial_path_3d.latlngs
        self.pylons = spatial_path_3d.pylons
        self.land_cost = spatial_path_3d.land_cost      
        self.pylon_cost = spatial_path_3d.pylon_cost
        self.tube_cost = spatial_path_3d.tube_cost
        self.tunneling_cost = spatial_path_3d.tunneling_cost
        self.total_cost = spatial_path_3d.total_cost
        self.trip_time = spatial_path_3d.min_time
        self.land_elevations = spatial_path_3d.land_elevations
        self.tube_elevations = spatial_path_3d.tube_elevations
        self.compute_comfort(velocity_profile)
    
    def get_time_and_cost(self):
        return [self.trip_time, self.total_cost]


class SpatiotemporalPathsSet4d(object):

    def build_velocity_profiles_v1(self, spatial_path_3d):
        #velocity_profile = self.velocity_builder(spatial_path_3d)
        #velocity_profiles = [velocity_profile]
        velocity_profiles = [0]
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
    IS_SKIPPED = cacher.SKIP_PATHS_4D
    
    def build_paths_sets(self, spatial_paths_3d):
        self.paths_sets = [SpatiotemporalPathsSet4d(spatial_path_3d,
                                                    self.velocity_builder)
                           for spatial_path_3d in spatial_paths_3d]

    def select_paths(self):
        paths_lists = [paths_set.paths for paths_set in self.paths_sets]
        paths = util.fast_concat(paths_lists)
        """"
        paths_times_and_costs = [path.get_time_and_cost() for path in paths]
        minimize_time = True
        minimize_cost = True
        front = paretofront.ParetoFront(paths_times_and_costs, minimize_time,
                                                               minimize_cost)
        selected_paths_indices = front.fronts_indices[-1]
        self.selected_paths = [paths[i] for i in selected_paths_indices]
        selected_times_and_costs = [path.get_time_and_cost() for path
                                    in self.selected_paths]
        """
        self.selected_paths = paths

    def __init__(self, spatial_paths_sets_3d, velocity_builder):
        self.velocity_builder = velocity_builder
        self.spatial_meta_data = spatial_paths_sets_3d.spatial_metadata
        self.build_paths_sets(spatial_paths_sets_3d.selected_paths)
        self.select_paths()


def get_spatiotemporal_paths_sets_4d(*args):
    spatiotemporal_paths_sets_4d = cacher.get_object(
                                        SpatiotemporalPathsSets4d.NAME,
                                        SpatiotemporalPathsSets4d,
                                        args,
                                        SpatiotemporalPathsSets4d.FLAG,
                                        SpatiotemporalPathsSets4d.IS_SKIPPED)
    return spatiotemporal_paths_sets_4d
