"""
citation: zacharybears.com
"""

from osgeo import gdal
from osgeo import osr
import struct

fp = "/home/ubuntu/Hyperloop/test/cache/us.tif"

def latlng_to_pixel(geotiff, latLonPairs):
    ds = gdal.Open(geotiff)
    gt = ds.GetGeoTransform()
    rb = ds.GetRasterBand(1)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srsLatLon = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srsLatLon,srs)
    vals = []
    for point in latLonPairs:
	(point[1],point[0],holder) = ct.TransformPoint(point[1],point[0])
        x = int((point[1] - gt[0])/gt[1])
        y = int((point[0] - gt[3])/gt[5])
	structval = rb.ReadRaster(x,y,1,1,buf_type=gdal.GDT_Float32)
	intval = struct.unpack('f', structval)
        val = intval[0]
        vals.append(val)          
    return vals

print(latlng_to_pixel(fp,[[34.05,-118.25]]))
