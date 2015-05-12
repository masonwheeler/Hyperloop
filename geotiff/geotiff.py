#From http://zacharybears.com/using-python-to-translate-latlon-locations-to-pixels-on-a-geotiff/

from osgeo import gdal
from osgeo import osr

import struct
import Image

fp = "/home/jonward/Devel/Loop/Hyperloop/geotiff/ca_south_NLCD_042800_erd.tif"

Costs = {11:10, #open water
         12:5,  #snow/ice
         24:10, #developed high intensity
         23:8,
         22:6,
         21:4,
         31:1,
         41:3,
         42:3,
         43:3,
         51:1,
         52:1,
         71:1,
         72:1,
         73:1,
         74:1,
         81:1,
         82:3,
         90:3,
         95:3} 

def latLonToPixel(geotiff, latLonPairs):
    ds = gdal.Open(geotiff)
    gt = ds.GetGeoTransform()
    rb = ds.GetRasterBand(1)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srsLatLon = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srsLatLon,srs)
    pixelPairs = []
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

#print(latLonToPixel(wd + "",[[34.05,-118.25]]))

gdal.Open(fp)

