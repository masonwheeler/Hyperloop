"""
Original Developer: Jonathan Ward
Purpose of Module: To download, cache, and access usgs elevation data.
Last Modified: 7/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Redesigned logic flow to save memory.
"""

# Standard Modules:
import math
import os
from osgeo import gdal
from osgeo import osr
from subprocess import call
import urllib
import zipfile

# Our Modules
import config
import geotiff
import util

#Experimental
import rasterio
import numpy as np
import affine
import pyproj


def get_bounding_coordinates(latlng_coord):
    """Get the top left corner of the latlng tile which the coord falls in
    """
    lat, lng = latlng_coord
    lat_bound = int(math.ceil(lat))
    lng_bound = int(math.ceil(abs(lng)))    
    return [lat_bound, lng_bound]

def get_coordstring(latlng_coord):
    """Get the string used to reference the latlng tile which the coord falls in
    """
    lat_bound, lng_bound = get_bounding_coordinates(latlng_coord)
    latstr, lngstr = "n" + str(lat_bound), "w" + str(lng_bound).zfill(3)
    coordstring = latstr + lngstr
    #print(coordstring)
    return coordstring

def get_img_file_name(coordstring):
    """Get the name of the img file which stores the tile's elevation data
    """
    img_filename = "img" + coordstring + "_13" + ".img"
    return img_filename

def file_exists(local_file_path):
    """Check whether a given file exists
    """
    return os.path.isfile(local_file_path)

def unzip_zipfile(zip_file_path, out_path, img_file_name):
    """Unzip the zipfile containing the img file which holds the elevation data
    """
    file_handle = open(zip_file_path, 'rb')
    zip_file_data = zipfile.ZipFile(file_handle)
    img_file_path = out_path + img_file_name
    img_exists = file_exists(img_file_path)
    if img_exists:
        if config.VERBOSE_MODE:
            print ".img file already exists"
    else:
        if config.VERBOSE_MODE:
            print "Unzipping folder..."
        for file_name in zip_file_data.namelist():
            if file_name == img_file_name:
                if config.VERBOSE_MODE:
                    print file_name + " extracted."
                zip_file_data.extract(file_name, out_path)
        file_handle.close()
        return 0

def img_to_geotiff(img_file_name, unzip_directory, coordstring):
    """Convert the img file containing the elevation data into a geotiff file
    """
    img_file_path = unzip_directory + img_file_name
    tif_file_path = unzip_directory + coordstring + ".tif"
    call(["gdal_translate", "-of", "Gtiff", img_file_path, tif_file_path])
    return tif_file_path

def geotiff_pixel_val(geotiff_file_path, lonlat_coord):
    """Get the pixel value at the given lon-lat coord in the geotiff
    """
    file_handle = gdal.Open(geotiff_file_path)    
    geo_transform = file_handle.GetGeoTransform()
    raster_band = file_handle.GetRasterBand(1)
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromWkt(file_handle.GetProjection())
    spatial_reference_lat_lon = spatial_reference.CloneGeogCS()
    coord_trans = osr.CoordinateTransformation(spatial_reference_lat_lon,
                                               spatial_reference)
    pixel_val = geotiff.get_pixel_val(coord_trans, geo_transform,
                                      raster_band, lonlat_coord)
    return pixel_val

def remove_file(file_path):
    """Delete the given file
    """
    os.remove(file_path)

def get_elevation(latlng_coord):
    """Gets the elevation at a given lat-lng coord
    """
    coordstring = get_coordstring(latlng_coord)
    coord_zipfile = coordstring + ".zip"
    coord_folder_name = coordstring + "/"

    url = config.USGS_FTP_PATH + coord_zipfile
    download_directory = config.CWD + config.USGS_FOLDER
    zip_file_path = download_directory + coord_zipfile
    unzip_directory = download_directory + coord_folder_name
    img_file_name = get_img_file_name(coordstring)
    img_file_path = unzip_directory + img_file_name
    geotiff_file_path = unzip_directory + coordstring + ".tif"

    if file_exists(geotiff_file_path):
        pass
    else:
        if file_exists(img_file_path):
            pass
        else:
            if file_exists(zip_file_path):
                pass
            else:
                util.smart_print("Not yet downloaded.")
                util.smart_print("Now downloading " + coord_zipfile + "...")
                util.smart_print("From " + str(url))
                urllib.urlretrieve(url, zip_file_path)
            unzip_zipfile(zip_file_path, unzip_directory, img_file_name)
            remove_file(zip_file_path)
        img_to_geotiff(img_file_name, unzip_directory, coordstring)
        remove_file(img_file_path)

    lonlat_coord = util.swap_pair(latlng_coord)
    pixel_val = geotiff_pixel_val(geotiff_file_path, lonlat_coord)
    return pixel_val

#V2

def partition_latlngs(latlngs):
    latlngs_partitions = [[]]
    last_bounds = get_bounding_coordinates(latlngs[0])   
    for latlng in latlngs:
        bounds = get_bounding_coordinates(latlng)
        if last_bounds == bounds:
            latlngs_partitions[-1].append(latlng)
        else:
            latlngs_partitions.append([latlng])
            last_bounds = bounds
    return latlngs_partitions

def geotiff_elevations(geotiff_file_path, lnglats):
    """Get the pixel value at the given lon-lat coord in the geotiff
    """
    #lngs = [lnglat[0] for lnglat in lnglats]
    #lats = [lnglat[1] for lnglat in lnglats]
    lngs, lats = zip(*lnglats)
    max_lng = max(lngs)
    min_lng = min(lngs)
    max_lat = max(lats)
    min_lat = min(lats)
    top_left_lnglat = [min_lng, max_lat]
    top_right_lnglat = [max_lng, max_lat]
    bottom_right_lnglat = [max_lng, min_lat]
    bottom_left_lnglat = [min_lng, min_lat]
    with rasterio.open(geotiff_file_path) as r:
        p1 = pyproj.Proj(r.crs)
        top_left_pixel = r.index(*top_left_lnglat)
        top_right_pixel = r.index(*top_right_lnglat)
        bottom_right_pixel = r.index(*bottom_right_lnglat)
        bottom_left_pixel = r.index(*bottom_left_lnglat)
        top = min(top_left_pixel[0], top_right_pixel[0])
        bottom = max(bottom_left_pixel[0], bottom_right_pixel[0])
        left = min(top_left_pixel[1], bottom_left_pixel[1])
        right = max(top_right_pixel[1], bottom_right_pixel[1])
        w = r.read(1, window=((top, bottom + 1), (left, right + 1)))
    untranslated_pixels = [r.index(*lnglat) for lnglat in lnglats]
    translated_pixels = [[pixel[0] - top, pixel[1] - left] for pixel
                                              in untranslated_pixels]
    xPixels, yPixels = np.transpose(np.array(translated_pixels))
    elevations_array = w[xPixels, yPixels]
    elevations = elevations_array.tolist()
    return elevations

def get_partition_elevations(latlngs_partition):
    """Gets the elevation at a given lat-lng coord
    """    
    coordstring = get_coordstring(latlngs_partition[0])
    coord_zipfile = coordstring + ".zip"
    coord_folder_name = coordstring + "/"

    url = config.USGS_FTP_PATH + coord_zipfile
    download_directory = config.CWD + config.USGS_FOLDER
    zip_file_path = download_directory + coord_zipfile
    unzip_directory = download_directory + coord_folder_name
    img_file_name = get_img_file_name(coordstring)
    img_file_path = unzip_directory + img_file_name
    geotiff_file_path = unzip_directory + coordstring + ".tif"

    if file_exists(geotiff_file_path):
        pass
    else:
        if file_exists(img_file_path):
            pass
        else:
            if file_exists(zip_file_path):
                pass
            else:
                util.smart_print("Not yet downloaded.")
                util.smart_print("Now downloading " + coord_zipfile + "...")
                util.smart_print("From " + str(url))
                urllib.urlretrieve(url, zip_file_path)
            unzip_zipfile(zip_file_path, unzip_directory, img_file_name)
            remove_file(zip_file_path)
        img_to_geotiff(img_file_name, unzip_directory, coordstring)
        remove_file(img_file_path)

    lnglats = util.swap_pairs(latlngs_partition)
    partition_elevations = geotiff_elevations(geotiff_file_path, lnglats)
    return partition_elevations

def get_elevations(latlngs):
    latlngs_partitions = partition_latlngs(latlngs)
    partitions_elevations = [get_partition_elevations(latlngs_partition)
                             for latlngs_partition in latlngs_partitions]
    elevations = util.fast_concat(partitions_elevations)
    return elevations
