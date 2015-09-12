"""
Original Developer: Jonathan Ward
Purpose of Module: To extract the pixel value corresponding to a given
                   longitude-latitude pair from a geotiff file.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: to clarify naming
"""

import numpy as np
from osgeo import gdal
import pyproj
import rasterio
import struct

def get_pixel_val(coord_transform, geotiff_data, raster_band, lonlat_coord):
    """Gets the pixel value corresponding to the given lon lat pair
    """
    lon, lat = lonlat_coord
    x_val, y_val, _ = coord_transform.TransformPoint(lon, lat)
    image_x = int((x_val - geotiff_data[0]) / geotiff_data[1])
    image_y = int((y_val - geotiff_data[3]) / geotiff_data[5])
    structval = raster_band.ReadRaster(image_x, image_y, 1, 1,
                                       buf_type=gdal.GDT_Float32)
    int_val = struct.unpack('f', structval)
    pixel_val = int_val[0]
    return pixel_val

def get_geotiff_pixel_vals_without_projection(geotiff_file_path, lnglats):
    """Get the pixel value at the given lon-lat coord in the geotiff w/o proj
    """
    lngs, lats = zip(*lnglats)
    max_lng = max(lngs)
    min_lng = min(lngs)
    max_lat = max(lats)
    min_lat = min(lats)
    with rasterio.open(geotiff_file_path) as r:
        top_left_row, top_left_col = r.index(min_lng, max_lat)        
        top_right_row, top_right_col = r.index(max_lng, max_lat)
        bottom_right_row, bottom_right_col = r.index(max_lng, min_lat)
        bottom_left_row, bottom_left_col = r.index(min_lng, min_lat)
        top_row = min(top_left_row, top_right_row)
        bottom_row = max(bottom_left_row, bottom_right_row)
        left_col = min(top_left_col, bottom_left_col)
        right_col = max(top_right_col, bottom_right_col)
        w = r.read(1, window=((top_row, bottom_row + 1),
                              (left_col, right_col + 1)))
    untranslated_pixels = [r.index(lnglat[0], lnglat[1]) for lnglat in lnglats]
    translated_pixels = [[pixel[0] - top_row, pixel[1] - left_col] for pixel
                                              in untranslated_pixels]
    xPixels, yPixels = np.transpose(np.array(translated_pixels))
    pixel_vals_array = w[xPixels, yPixels]
    pixel_vals = pixel_vals_array.tolist()
    return pixel_vals

def get_geotiff_pixel_vals_with_projection(geotiff_file_path, lnglats):
    """Get the pixel value at the given lon-lat coord in the geotiff with proj
    """
    lngs, lats = zip(*lnglats)
    max_lng = max(lngs)
    min_lng = min(lngs)
    max_lat = max(lats)
    min_lat = min(lats)
    with rasterio.open(geotiff_file_path) as r:
        p1 = pyproj.Proj(r.crs)
        top_left_x, top_left_y = p1(min_lng, max_lat)
        top_right_x, top_right_y = p1(max_lng, max_lat)
        bottom_right_x, bottom_right_y = p1(max_lng, min_lat)
        bottom_left_x, bottom_left_y = p1(min_lng, min_lat)
        top_left_row, top_left_col = r.index(top_left_x, top_left_y)
        top_right_row, top_right_col = r.index(top_right_x, top_right_y)
        bottom_right_row, bottom_right_col = r.index(bottom_right_x,
                                                     bottom_right_y)
        bottom_left_row, bottom_left_col = r.index(bottom_left_x,
                                                   bottom_left_y)
        top_row = min(top_left_row, top_right_row)
        bottom_row = max(bottom_left_row, bottom_right_row)
        left_col = min(top_left_col, bottom_left_col)
        right_col = max(top_right_col, bottom_right_col)
        w = r.read(1, window=((top_row, bottom_row + 1),
                              (left_col, right_col + 1)))
    geospatials = [p1(lnglat[0], lnglat[1]) for lnglat in lnglats]
    untranslated_pixels = [r.index(geospatial[0], geospatial[1]) for geospatial
                                                                 in geospatials]
    translated_pixels = [[pixel[0] - top_row, pixel[1] - left_col] for pixel
                                              in untranslated_pixels]
    xPixels, yPixels = np.transpose(np.array(translated_pixels))
    pixel_vals_array = w[xPixels, yPixels]
    pixel_vals = pixel_vals_array.tolist()
    return pixel_vals

