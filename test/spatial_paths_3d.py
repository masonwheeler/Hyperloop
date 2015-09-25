"""
Original Developer:
    Jonathan Ward
"""

# Custom Modules:
import cacher
import config
import curvature
import paretofront
import util
import velocity


class SpatialPath3d(object):

    def compute_min_time_and_total_cost(self, spatial_curvature_array,
                                                 tube_curvature_array,
                                                          arc_lengths):
        max_allowed_vels_lateral = \
            curvature.lateral_curvature_array_to_max_allowed_vels(
                                                    spatial_curvature_array)
        max_allowed_vels_vertical = \
            curvature.vertical_curvature_array_to_max_allowed_vels(
                                                    tube_curvature_array)
        effective_max_allowed_vels = np.minimum(max_allowed_vels_vertical,
                                                max_allowed_vels_lateral)
        time_checkpoints = \
            velocity.velocities_by_arc_length_to_time_checkpoints(
                            effective_max_allowed_vels, arc_lengths)
        self.min_time = time_checkpoints[-1]
        self.total_cost = self.pylon_cost + self.tube_cost + self.land_cost


    def __init__(self, tube_profile, spatial_path_2d):
        self.land_cost = spatial_path_2d.land_cost
        self.latlngs = spatial_path_2d.latlngs
        self.geospatials = spatial_path_2d.geospatials
        self.pylons = tube_profile.pylons
        self.pylon_cost = tube_profile.pylon_cost
        self.tube_coords = tube_profile.tube_coords
        self.tube_cost = tube_profile.tube_cost
        self.land_elevations = tube_profile.land_elevations
        self.arc_lengths = tube_profile.arc_lengths
        self.min_time = tube_profile.min_time
        print "min time"
        print self.min_time / 60.0

    def get_time_and_cost(self):
        total_cost = self.land_cost + self.pylon_cost + self.tube_cost
        return [self.min_time, total_cost]


class SpatialPathsSet3d(object):
  
    NUM_TUBE_PROFILES = 5

    def build_tube_profiles_v1(self, tube_builder, elevation_profile):
        tube_profiles = []
        #tube_profile = tube_builder(elevation_profile, max_curvature=0)
        #tube_profiles.append(tube_profile)
        for i in range(self.NUM_TUBE_PROFILES):
            max_curvature = (tube_builder.DEFAULT_MAX_CURVATURE * 
                            (float(i) / (float(self.NUM_TUBE_PROFILES) * 250.0)))
            tube_profile = tube_builder(elevation_profile,
                              max_curvature=max_curvature)
            tube_profiles.append(tube_profile)
        return tube_profiles

    def build_paths(self, spatial_path_2d, tube_profiles):
        self.paths = [SpatialPath3d(tube_profile, spatial_path_2d)
                      for tube_profile in tube_profiles]

    def __init__(self, spatial_path_2d, tube_builder):
        elevation_profile = spatial_path_2d.elevation_profile 
        tube_profiles = self.build_tube_profiles_v1(tube_builder,
                                                    elevation_profile)
        self.build_paths(spatial_path_2d, tube_profiles)


class SpatialPathsSets3d(object):

    NAME = "spatial_paths_3d"
    FLAG = cacher.SPATIAL_PATHS_3D_FLAG
    IS_SKIPPED = cacher.SKIP_PATHS_3D

    def build_paths_sets(self, spatial_paths_2d, tube_builder):
        print("Num paths 2d: " + str(len(spatial_paths_2d)))
        self.paths_sets = [SpatialPathsSet3d(spatial_path_2d, tube_builder)
                           for spatial_path_2d in spatial_paths_2d]      
        
    def select_paths(self):
        paths_lists = [paths_set.paths for paths_set in self.paths_sets]
        paths = util.fast_concat(paths_lists)
        print "num paths 3d: " + str(len(paths))
        paths_times_and_costs = [path.get_time_and_cost() for path in paths]
        minimize_time = True
        minimize_cost = True
        front = paretofront.ParetoFront(paths_times_and_costs, minimize_time,
                                                               minimize_cost)
        ##print "all times and costs"
        ##print paths_times_and_costs
        selected_paths_indices = front.fronts_indices[-1]
        self.selected_paths = [paths[i] for i in selected_paths_indices]
        ##selected_times_and_costs = [path.get_time_and_cost() for path
        ##                            in self.selected_paths]
        ##print "selected times and costs"
        ##print selected_times_and_costs
        print "num paths 3d selected: " + str(len(self.selected_paths))

    def __init__(self, spatial_paths_set_2d):
        self.start = spatial_paths_set_2d.start
        self.end = spatial_paths_set_2d.end
        self.start_latlng = spatial_paths_set_2d.start_latlng
        self.end_latlng = spatial_paths_set_2d.end_latlng
        tube_builder = spatial_paths_set_2d.tube_builder
        self.undersampling_factor = spatial_paths_set_2d.UNDERSAMPLING_FACTOR
        self.build_paths_sets(spatial_paths_set_2d.paths, tube_builder)
        self.select_paths()
        
                                                             
def get_spatial_paths_sets_3d(*args):
    spatial_paths_set_3d = cacher.get_object(SpatialPathsSets3d.NAME,
                                             SpatialPathsSets3d,
                                             args,
                                             SpatialPathsSets3d.FLAG,
                                             SpatialPathsSets3d.IS_SKIPPED)
    return spatial_paths_set_3d
 
