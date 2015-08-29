"""
Original Developer: Jonathan Ward
Purpose of Module: To extract the pixel value corresponding to a given
                   longitude-latitude pair from a geotiff file.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: to clarify naming
"""


import struct
from osgeo import gdal

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
