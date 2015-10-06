"""
Original Developer: Jonathan Ward
Purpose of Module: To obtain the elevation of each coordinate in
                   a list of latitude longitude coords.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify module usage.
"""

# Our Modules
import parameters
import usgs
import util

class ElevationProfile(object):
    
    def get_land_elevations(self):
        land_elevations = [usgs.get_elevation(latlng)
                           for latlng in self.latlngs]
        return land_elevations
    
    def get_land_elevations_v2(self):
        land_elevations = usgs.get_elevations(self.latlngs)
        return land_elevations

    def __init__(self, geospatials, latlngs, arc_lengths,
                 elevation_point_spacing,
                 land_elevations=None, geospatials_partitions=None):
        self.geospatials = geospatials
        self.latlngs = latlngs
        self.arc_lengths = arc_lengths
        self.elevation_point_spacing = elevation_point_spacing
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
        elevation_point_spacing = (parameters.PYLON_SPACING / 
                                   elevation_points_to_pylon_points_ratio)
        geospatials, arc_lengths = util.build_grid(
                                      start_geospatial,
                                        end_geospatial,
                               elevation_point_spacing)
        latlngs = geospatials_to_latlngs(geospatials)
        data = cls(geospatials, latlngs, arc_lengths, elevation_point_spacing)
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
        merged_land_elevations = util.smart_concat(
                                    elevation_profile_a.land_elevations,
                                    elevation_profile_b.land_elevations)
        arc_length_offset = elevation_profile_a.arc_lengths[-1]
        shifted_arc_lengths_b = [arc_length + arc_length_offset for arc_length
                                 in elevation_profile_b.arc_lengths]
        merged_arc_lengths = util.smart_concat(elevation_profile_a.arc_lengths,
                                                         shifted_arc_lengths_b)
        data = cls(merged_geospatials, merged_latlngs, merged_arc_lengths, 
                   land_elevations=merged_land_elevations,
                   geospatials_partitions=merged_geospatials_partitions)
        return data
    
