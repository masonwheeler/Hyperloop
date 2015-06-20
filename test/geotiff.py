from osgeo import gdal
from osgeo import osr
import struct

def pixel_val(ct, gt, rb, lonlatCoord):
    xVal, yVal, zVal = ct.TransformPoint(*lonlatCoord)
    x = int((xVal - gt[0]) / gt[1])
    y = int((yVal - gt[3]) / gt[5])
    structval = rb.ReadRaster(x,y,1,1,buf_type=gdal.GDT_Float32)
    intVal = struct.unpack('f', structval)
    pixelVal = intVal[0]
    return pixelVal
