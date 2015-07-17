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

def pixel_val(coordTransform, geotiffData, rasterBand, lonlatCoord):
    xVal, yVal, zVal = coordTransform.TransformPoint(*lonlatCoord)
    x = int((xVal - geotiffData[0]) / geotiffData[1])
    y = int((yVal - geotiffData[3]) / geotiffData[5])
    structval = rasterBand.ReadRaster(x, y, 1, 1, buf_type=gdal.GDT_Float32)
    intVal = struct.unpack('f', structval)
    pixelVal = intVal[0]
    return pixelVal
