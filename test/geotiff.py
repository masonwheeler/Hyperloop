"""
Original Developer: Jonathan Ward
Purpose of Module: To extract the pixel value corresponding to a given
                   longitude-latitude pair from a geotiff file. 
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: to clarify naming
"""

from osgeo import gdal
from osgeo import osr
import struct


def pixel_val(coord_transform, geotiff_data, raster_band, lonlat_coord):
    x_val, y_val, z_val = coord_transform.TransformPoint(*lonlat_coord)
    x = int((x_val - geotiff_data[0]) / geotiff_data[1])
    y = int((y_val - geotiff_data[3]) / geotiff_data[5])
    structval = raster_band.ReadRaster(x, y, 1, 1, buf_type=gdal.GDT_Float32)
    int_val = struct.unpack('f', structval)
    pixel_val = int_val[0]
    return pixel_val
