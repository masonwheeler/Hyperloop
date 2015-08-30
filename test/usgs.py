"""
Original Developer: Jonathan Ward
Purpose of Module: To download, cache, and access usgs elevation data.
Last Modified: 7/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Redesigned logic flow to save memory.
"""

# Standard Modules:
from osgeo import gdal
from osgeo import osr
import urllib
import zipfile
import os
import math
from subprocess import call

# Our Modules
import config
import util
import geotiff


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
                urllib.urlretrieve(url, zip_file_path)
            unzip_zipfile(zip_file_path, unzip_directory, img_file_name)
            remove_file(zip_file_path)
        img_to_geotiff(img_file_name, unzip_directory, coordstring)
        remove_file(img_file_path)

    lonlat_coord = util.swap_pair(latlng_coord)
    pixel_val = geotiff_pixel_val(geotiff_file_path, lonlat_coord)

    return pixel_val
