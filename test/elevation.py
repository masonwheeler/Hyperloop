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
import srtm
import usgs
import util


elevationDownloader = srtm.SRTMDownloader()
elevationDownloader.loadFileList()
lastSRTMTile = None
lastBoundingLatLng = None

class ElevationProfile(object):
    
    def get_land_elevations_usgs(self):
        land_elevations_list = [usgs.get_elevation(latlng)
                                for latlng in self.latlngs]
        land_elevations = np.array(land_elevations_list)
        return land_elevations

    def get_land_elevations_srtm(self):

        global lastBoundingLatLng 
        global lastSRTMTile 

        bounding_latlngs = [srtm.SRTMTile.get_bounding_coords(latlng)
                            for latlng in self.latlngs]
        bounding_latlngs_unchanged = [bounding_latlng == lastBoundingLatLng 
                                      for bounding_latlng in bounding_latlngs]
        if all(bounding_latlngs_unchanged):
            tiles = [lastSRTMTile]            
            land_elevations = [tile.getAltitudeFromLatLon(latlng[0], latlng[1])
                               for latlng in self.latlngs]
        else:
            bounding_latlngs_lists = [[]]
            last_bounding_latlng = bounding_latlngs[0]
            for bounding_latlng in bounding_latlngs:    
                if bounding_latlng != last_bounding_latlng:
                    bounding_latlngs_lists.append([])
                    bounding_latlngs_lists[-1].append(bounding_latlng)
                    last_bounding_latlng = bounding_latlng
                else:
                    bounding_latlngs_lists[-1].append(bounding_latlng)
            tile_latlngs = [latlngs_list[0] for latlngs_list 
                            in bounding_latlngs_lists]
            tiles = [elevationDownloader.getTile(tile_latlng[0], tile_latlng[1]) 
                     for tile_latlng in tile_latlngs]
            bounding_latlngs_lists_lengths = [len(latlngs_list) for latlngs_list
                                              in bounding_latlngs_lists]
            last_index = 0
            latlngs_lists = []
            for list_length in bounding_latlngs_lists_lengths:
                latlngs_list = self.latlngs[last_index:last_index + list_length]
                latlngs_lists.append(latlngs_list)
                last_index += list_length

            land_elevations_lists = []
            for i in range(len(latlngs_lists)):
                tile = tiles[i]
                latlngs_list = latlngs_lists[i]
                land_elevations_list = [tile.getAltitudeFromLatLon(latlng[0], 
                                                                   latlng[1])
                                        for latlng in latlngs_list]
                land_elevations_lists.append(land_elevation_list)
            land_elevations = util.fast_concat(land_elevations_lists)

        lastBoundingLatlng = bounding_latlngs[-1]
        lastSRTMTile = tiles[-1]
        return land_elevations

    def __init__(self, geospatials, latlngs, arc_lengths,
                 land_elevations=None, geospatials_partitions=None):
        self.geospatials = geospatials
        self.latlngs = latlngs
        self.arc_lengths = arc_lengths
        if geospatials_partitions == None:
            geospatials_partitions = [geospatials]
        self.geospatials_partitions = geospatials_partitions
        if land_elevations == None:
            self.land_elevations = self.get_land_elevations_srtm()
            #self.land_elevations = self.get_land_elevations_usgs()
        else:
            self.land_elevations = land_elevations

    @classmethod
    def init_from_geospatial_pair(cls, start_geospatial, end_geospatial, 
          geospatials_to_latlngs, elevation_points_to_pylon_points_ratio):
        arc_length_step_size = (parameters.PYLON_SPACING / 
                                   elevation_points_to_pylon_points_ratio)
        geospatials, arc_lengths = util.build_grid(start_geospatial,
                               end_geospatial, arc_length_step_size)
        latlngs = geospatials_to_latlngs(geospatials)
        data = cls(geospatials, latlngs, arc_lengths)
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
        merged_geospatials = np.vstack((elevation_profile_a.geospatials,
                                        elevation_profile_b.geospatials[1:]))
        merged_latlngs = np.vstack((elevation_profile_a.latlngs,
                                    elevation_profile_b.latlngs[1:]))
        merged_land_elevations = util.glue_array_pair(
                                    elevation_profile_a.land_elevations,
                                    elevation_profile_b.land_elevations)
        merged_arc_lengths = util.shift_and_glue_array_pair(
                            elevation_profile_a.arc_lengths,
                            elevation_profile_b.arc_lengths)
        data = cls(merged_geospatials, merged_latlngs, merged_arc_lengths, 
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
          undersampled_geospatials.tolist(), undersampled_latlngs.tolist(),
          undersampled_arc_lengths.tolist(), undersampled_arc_length_step_size)
        return undersampled_elevation_profile
