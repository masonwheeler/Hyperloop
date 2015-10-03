"""
Original Developer:
    Jonathan Ward
"""

# Standard Modules:
import numpy as np

# Custom Modules:
import cacher
import config
import curvature
import parameters
import paretofront
import util
import reparametrize_speed


class SpatialPath3d(object):

    def compute_min_time(self, spatial_curvature_array,
                                  tube_curvature_array,
                                           arc_lengths):
        max_allowed_vels_lateral = \
            curvature.lateral_curvature_array_to_max_allowed_vels(
                                                    spatial_curvature_array)
        max_allowed_vels_vertical = \
            curvature.vertical_curvature_array_to_max_allowed_vels(
                                                    tube_curvature_array)
        effective_max_allowed_speeds_by_arc_length = np.minimum(
            max_allowed_vels_vertical, max_allowed_vels_lateral)
        time_step_size = 1 #second times
        speeds_by_time, time_elapsed = \
        reparametrize_speed.constrain_and_reparametrize_speeds_by_arc_length(
                     effective_max_allowed_speeds_by_arc_length, arc_lengths,
                           time_step_size, parameters.MAX_LONGITUDINAL_ACCEL)
        return time_elapsed


    def __init__(self, tube_profile, spatial_path_2d):
        self.land_cost = spatial_path_2d.land_cost
        self.pylon_cost = tube_profile.pylon_cost
        self.tube_cost = tube_profile.tube_cost
        self.tunneling_cost = tube_profile.tunneling_cost        
        self.latlngs = spatial_path_2d.latlngs
        #self.pylons = tube_profile.pylons
        self.pylons = []
        self.tube_coords = []
        self.land_elevations = []#tube_profile.land_elevations
        self.arc_lengths = []#tube_profile.arc_lengths
        self.spatial_curvature_array = spatial_path_2d.spatial_curvature_array
        self.tube_curvature_array = tube_profile.tube_curvature_array
        self.min_time = self.compute_min_time(self.spatial_curvature_array,
                                                self.tube_curvature_array,
                                                         self.arc_lengths)
        #self.min_time = spatial_path_2d.min_time
        #self.total_cost = spatial_path_2d.total_cost

    def fetch_min_time_and_total_cost(self):
        #print "min time in secs: " + str(self.min_time)
        min_time = round(self.min_time / 60.0, 2)
        #print "rounded min time in mins: " + str(min_time)
        #print self.total_cost
        total_cost = round(self.total_cost / 10.0**9, 5)
        #print total_cost
        return [min_time, total_cost]


class SpatialPathsSet3d(object):
  
    NUM_TUBE_PROFILES = 5

    def build_tube_profiles_v1(self, tube_builder, elevation_profile):
        tube_profiles = [0]
        #tube_profile = tube_builder(elevation_profile, max_curvature=0)
        #tube_profiles.append(tube_profile)
        #for i in range(self.NUM_TUBE_PROFILES):
        #    max_curvature = (tube_builder.DEFAULT_MAX_CURVATURE * 
        #                    (float(i) / (float(self.NUM_TUBE_PROFILES) * 250.0)))
        #    tube_profile = tube_builder(elevation_profile,
        #                      max_curvature=max_curvature)
        #    tube_profiles.append(tube_profile)
        return tube_profiles

    def build_paths(self, spatial_path_2d, tube_profiles):
        self.paths = [SpatialPath3d(tube_profile, spatial_path_2d)
                      for tube_profile in tube_profiles]

    def __init__(self, spatial_path_2d, tube_builder):
        elevation_profile = 0#spatial_path_2d.elevation_profile 
        tube_profiles = self.build_tube_profiles_v1(tube_builder,
                                                    elevation_profile)
        self.build_paths(spatial_path_2d, tube_profiles)


class SpatialPathsSets3d(object):

    NAME = "spatial_paths_3d"
    FLAG = cacher.SPATIAL_PATHS_3D_FLAG
    IS_SKIPPED = cacher.SKIP_PATHS_3D

    def build_paths_sets(self, spatial_paths_2d, tube_builder):
        print("Num paths 2d: " + str(len(spatial_paths_2d)))
        paths_sets = [SpatialPathsSet3d(spatial_path_2d, tube_builder)
                           for spatial_path_2d in spatial_paths_2d]
        return paths_sets
        
    def select_paths(self, paths_sets):
        paths_lists = [paths_set.paths for paths_set in paths_sets]
        paths = util.fast_concat(paths_lists)
        paths = sorted(paths, key=lambda p: p.total_cost)
        print "num paths 3d: " + str(len(paths))
        paths_times_and_costs = [path.fetch_min_time_and_total_cost()
                                 for path in paths]
        minimize_time = True
        minimize_cost = True
        front = paretofront.ParetoFront(paths_times_and_costs, minimize_time,
                                                               minimize_cost)
        optimal_paths_indices = front.fronts_indices[-1]
        optimal_paths = [paths[i] for i in optimal_paths_indices]
        #optimal_paths = sorted(optimal_paths, key=lambda p: p.total_cost)
        #paths_times_and_costs = [path.fetch_min_time_and_total_cost()
        #                         for path in optimal_paths]
        #minimize_time = True
        #minimize_cost = True
        #front = paretofront.ParetoFront(paths_times_and_costs, minimize_time,
        #                                                       minimize_cost)
        #optimal_paths_indices = front.fronts_indices[-1]
        #optimal_paths = [paths[i] for i in optimal_paths_indices]
        sorted_paths = sorted(optimal_paths, key=lambda p: p.total_cost)
        self.selected_paths = sorted_paths
        print "num paths 3d selected: " + str(len(self.selected_paths))

    def __init__(self, spatial_paths_set_2d):
        self.start = spatial_paths_set_2d.start
        self.end = spatial_paths_set_2d.end
        self.start_latlng = spatial_paths_set_2d.start_latlng
        self.end_latlng = spatial_paths_set_2d.end_latlng
        tube_builder = spatial_paths_set_2d.tube_builder
        self.undersampling_factor = spatial_paths_set_2d.UNDERSAMPLING_FACTOR
        paths_sets = self.build_paths_sets(spatial_paths_set_2d.paths,
                                                         tube_builder)
        self.select_paths(paths_sets)
        
                                                             
def get_spatial_paths_sets_3d(*args):
    spatial_paths_set_3d = cacher.get_object(SpatialPathsSets3d.NAME,
                                             SpatialPathsSets3d,
                                             args,
                                             SpatialPathsSets3d.FLAG,
                                             SpatialPathsSets3d.IS_SKIPPED)
    return spatial_paths_set_3d
 
