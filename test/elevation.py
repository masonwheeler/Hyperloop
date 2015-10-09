"""
Original Developer: Jonathan Ward
Purpose of Module: To obtain the elevation of each coordinate in
                   a list of latitude longitude coords.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify module usage.
"""

# Standard Modules
import numpy as np

# Custom Modules
import parameters
import usgs
import util

class ElevationProfile(object):
    
    def get_land_elevations(self):
        land_elevations_list = [usgs.get_elevation(latlng)
                                for latlng in self.latlngs]
        land_elevations = np.array(land_elevations_list)
        return land_elevations
    
    def get_land_elevations_v2(self):
        land_elevations = usgs.get_elevations(self.latlngs)
        return land_elevations

    def __init__(self, geospatials, latlngs, arc_lengths,
                 arc_length_step_size,
                 land_elevations=None, geospatials_partitions=None):
        self.geospatials = geospatials
        self.latlngs = latlngs
        self.arc_lengths = arc_lengths
        self.arc_length_step_size = arc_length_step_size
        if geospatials_partitions == None:
            geospatials_partitions = [geospatials]
        self.geospatials_partitions = geospatials_partitions
        if land_elevations == None:
            self.land_elevations = self.get_land_elevations()
        else:
            self.land_elevations = land_elevations

    @classmethod
    def init_from_geospatial_pair(cls, start_geospatial, end_geospatial, 
          geospatials_to_latlngs, elevation_points_to_pylon_points_ratio):
        arc_length_step_size = (parameters.PYLON_SPACING / 
                                   elevation_points_to_pylon_points_ratio)
        geospatials, arc_lengths = util.build_grid(
                                      start_geospatial,
                                        end_geospatial,
                                  arc_length_step_size)
        latlngs = geospatials_to_latlngs(geospatials)
        data = cls(geospatials, latlngs, arc_lengths, arc_length_step_size)
        return data        

    @classmethod
    def merge_elevation_profiles(cls, elevation_profile_a, elevation_profile_b):
        if (elevation_profile_a.geospatials_partitions != None and
            elevation_profile_b.geospatials_partitions != None):      
            merged_geospatials_partitions = (
                    elevation_profile_a.geospatials_partitions +
                    elevation_profile_b.geospatials_partitions)
        else:
            merged_geospatials_partitions = None
        merged_geospatials = util.smart_concat(elevation_profile_a.geospatials,
                                               elevation_profile_b.geospatials)
        merged_latlngs = util.smart_concat(elevation_profile_a.latlngs,
                                           elevation_profile_b.latlngs)
        merged_land_elevations = util.smart_concat_array(
                                    elevation_profile_a.land_elevations,
                                    elevation_profile_b.land_elevations)
        merged_arc_lengths = util.offset_concat(elevation_profile_a.arc_lengths,
                                                elevation_profile_b.arc_lengths)
        arc_length_step_size = elevation_profile_a.arc_length_step_size
        data = cls(merged_geospatials, merged_latlngs, merged_arc_lengths, 
                   arc_length_step_size,
                   land_elevations=merged_land_elevations,
                   geospatials_partitions=merged_geospatials_partitions)
        return data

    def undersample(self, undersampling_factor):
        undersampled_geospatials = self.geospatials[::undersampling_factor]
        undersampled_latlngs = self.latlngs[::undersampling_factor]
        undersampled_arc_lengths = self.arc_lengths[::undersampling_factor]
        undersampled_arc_length_step_size = (self.arc_length_step_size *
                                             undersampling_factor)
        undersampled_elevation_profile = ElevationProfile(
            undersampled_geospatials, undersampled_latlngs,
            undersampled_arc_lengths, undersampled_arc_length_step_size)
        return undersampled_elevation_profile
