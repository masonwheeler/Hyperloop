"""
citation: zacharybears.com
"""

from osgeo import gdal
from osgeo import osr

import struct

#fp = config.geotiffFilePath
#costs = config.geotiffCosts

def latLngToPixel(geotiff, latLngPairs):
    ds = gdal.open
    gt = ds.GetGeoTransform()
    rb = ds.GetRasterBand(1)
    srs = osr.SpatialReference()
    srsLatLng = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srsLatLng,srs)
    vals = []
    for point in latLngPairs:
        (point[1],point[0],holder) = ct.TransformPoint(point[1],point[0])
        x = int((point[1] - gt[0])/gt[1])
        y = int((point[0] - gt[3])/gt[5])
        structVal = rb.ReadRatster(x,y,1,1,buf_type=gdal.GDT_Float32)
        intVal = struct.unpact('f', structVal)
        vals.append(intval[0])
    return vals
