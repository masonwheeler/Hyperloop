"""
Original Developer: Jonathan Ward
"""

# Standard Modules
import numpy as np

# Custom Modules:
import cacher
#import sperling_comfort
import paretofront
import naive_passenger_frame as passenger_frame
import util


class SpatiotemporalPath4d(object):
        
    def compute_comfort(self, speed_profile, spatial_path_3d):
        comfort_profile = []
        comfort_rating = 0
        return [comfort_profile, comfort_rating]

    def __init__(self, speed_profile, spatial_path_3d):
        comfort_profile, comfort_rating = self.compute_comfort(speed_profile,
                                                             spatial_path_3d)
        self.speeds_by_time = speed_profile.speeds_by_time
        self.accels_by_time = speed_profile.accels_by_time
        self.comfort_profile = comfort_profile
        self.comfort_rating = comfort_rating
        self.latlngs = spatial_path_3d.latlngs
        self.pylons = spatial_path_3d.pylons
        self.land_cost = spatial_path_3d.land_cost      
        self.pylon_cost = spatial_path_3d.pylon_cost
        self.tube_cost = spatial_path_3d.tube_cost
        self.tunneling_cost = spatial_path_3d.tunneling_cost
        self.total_cost = spatial_path_3d.total_cost
        self.trip_time = speed_profile.trip_time
        self.land_elevations = spatial_path_3d.land_elevations
        self.tube_elevations = spatial_path_3d.tube_elevations
    
    def get_time_and_cost(self):
        return [self.trip_time, self.total_cost]


class SpatiotemporalPathsSet4d(object):

    def build_speed_profiles(self, spatial_path_3d, speed_profile_builder):
        speed_profile = speed_profile_builder(spatial_path_3d)
        speed_profiles = [speed_profile]
        return speed_profiles

    def build_paths(self, spatial_path_3d, speed_profiles):
        paths = [SpatiotemporalPath4d(speed_profile, spatial_path_3d)
                 for speed_profile in speed_profiles]
        return paths
    
    def __init__(self, spatial_path_3d, speed_profile_builder):
        speed_profiles = self.build_speed_profiles(spatial_path_3d,
                                                   speed_profile_builder)
        self.paths = self.build_paths(spatial_path_3d, speed_profiles)


class SpatiotemporalPathsSets4d(object):
    
    NAME = "spatiotemporal_paths_4d"
    FLAG = cacher.SPATIOTEMPORAL_PATHS_4D_FLAG
    IS_SKIPPED = cacher.SKIP_PATHS_4D
    
    def build_paths_sets(self, spatial_paths_3d, speed_profile_builder):
        paths_sets = [SpatiotemporalPathsSet4d(spatial_path_3d,
                                               speed_profile_builder)
                      for spatial_path_3d in spatial_paths_3d]
        return paths_sets

    def select_paths(self, paths_sets):
        paths_lists = [paths_set.paths for paths_set in paths_sets]
        selected_paths = util.fast_concat(paths_lists)
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
        return selected_paths

    def __init__(self, spatial_paths_sets_3d, speed_profile_builder):
        self.spatial_metadata = spatial_paths_sets_3d.spatial_metadata
        paths_sets = self.build_paths_sets(spatial_paths_sets_3d.selected_paths,
                                           speed_profile_builder)
        self.selected_paths = self.select_paths(paths_sets)


def get_spatiotemporal_paths_sets_4d(*args):
    spatiotemporal_paths_sets_4d = cacher.get_object(
                                        SpatiotemporalPathsSets4d.NAME,
                                        SpatiotemporalPathsSets4d,
                                        args,
                                        SpatiotemporalPathsSets4d.FLAG,
                                        SpatiotemporalPathsSets4d.IS_SKIPPED)
    return spatiotemporal_paths_sets_4d
